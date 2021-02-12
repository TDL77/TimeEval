import asyncio
import datetime as dt
import json
import logging
import socket
import subprocess
from enum import Enum
from pathlib import Path
from typing import Callable, Any
from typing import List, Tuple, Dict, Optional

import numpy as np
import pandas as pd
import tqdm
from distributed.client import Future

from .adapters.docker import DockerTimeoutError
from .algorithm import Algorithm
from .constants import RESULTS_CSV
from .datasets import Datasets
from .experiments import Experiments, Experiment
from .remote import Remote, RemoteConfiguration


class Status(Enum):
    OK = 0
    ERROR = 1
    TIMEOUT = 2


class TimeEval:
    RESULT_KEYS = ("algorithm",
                   "collection",
                   "dataset",
                   "score",
                   "preprocess_time",
                   "main_time",
                   "postprocess_time",
                   "status",
                   "error_message",
                   "repetition")

    DEFAULT_RESULT_PATH = Path("./results")

    def __init__(self,
                 dataset_mgr: Datasets,
                 datasets: List[Tuple[str, str]],
                 algorithms: List[Algorithm],
                 results_path: Path = DEFAULT_RESULT_PATH,
                 distributed: bool = False,
                 remote_config: Optional[RemoteConfiguration] = None,
                 repetitions: int = 1,
                 disable_progress_bar: bool = False):
        self.dmgr = dataset_mgr
        start_date: str = dt.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        self.results_path = results_path.absolute() / start_date
        self.exps = Experiments(datasets, algorithms, self.results_path, repetitions=repetitions)

        self.distributed = distributed
        self.remote_config = remote_config or RemoteConfiguration()
        self.results = pd.DataFrame(columns=TimeEval.RESULT_KEYS)
        self.disable_progress_bar = disable_progress_bar

        if self.distributed:
            self.remote = Remote(disable_progress_bar=self.disable_progress_bar, remote_config=self.remote_config)
            self.results["future_result"] = np.nan

    def _get_dataset_path(self, name: Tuple[str, str]) -> Path:
        return self.dmgr.get_dataset_path(name, train=False)

    def _run(self):
        for exp in tqdm.tqdm(self.exps, desc=f"Evaluating", disable=self.distributed or self.disable_progress_bar):
            try:
                future_result: Optional[Future] = None
                result: Optional[Dict] = None

                dataset_path = self._get_dataset_path(exp.dataset)

                if self.distributed:
                    future_result = self.remote.add_task(exp.evaluate, dataset_path)
                else:
                    result = exp.evaluate(dataset_path)
                self._record_results(exp, result=result, future_result=future_result)

            except Exception as e:
                logging.exception(
                    f"Exception occurred during the evaluation of {exp.algorithm.name} on the dataset {exp.dataset}:")
                f: asyncio.Future = asyncio.Future()
                f.set_result({
                    "score": np.nan,
                    "main_time": np.nan,
                    "preprocess_time": np.nan,
                    "postprocess_time": np.nan
                })
                self._record_results(exp, future_result=f, status=Status.ERROR, error_message=str(e))

    def _record_results(self,
                        exp: Experiment,
                        result: Optional[Dict] = None,
                        future_result: Optional[Future] = None,
                        status: Status = Status.OK,
                        error_message: Optional[str] = None):
        new_row = {
            "algorithm": exp.algorithm.name,
            "collection": exp.dataset_collection,
            "dataset": exp.dataset_name,
            "status": status.name,
            "error_message": error_message,
            "repetition": exp.repetition,
            "hyper_params": json.dumps(exp.params),
            "hyper_params_id": exp.params_id
        }
        if result is not None and future_result is None:
            new_row.update(result)
        elif result is None and future_result is not None:
            new_row.update({"future_result": future_result})
        self.results = self.results.append(new_row, ignore_index=True)
        self.results.replace(to_replace=[None], value=np.nan, inplace=True)

    def _resolve_future_results(self):
        self.remote.fetch_results()

        result_keys = ["score", "preprocess_time", "main_time", "postprocess_time"]
        status_keys = ["status", "error_message"]
        keys = result_keys + status_keys

        def get_future_result(f: Future) -> Tuple:
            try:
                r = f.result()
                return tuple(r[k] for k in result_keys) + (Status.OK, None)
            except DockerTimeoutError as e:
                logging.exception(f"Exception {str(e)} occurred remotely.")
                status = Status.TIMEOUT
                error_message = str(e)
            except Exception as e:
                logging.exception(f"Exception {str(e)} occurred remotely.")
                status = Status.ERROR
                error_message = str(e)

            return tuple(np.nan for _ in result_keys) + (status, error_message)

        self.results[keys] = self.results["future_result"].apply(get_future_result).tolist()
        self.results = self.results.drop(['future_result'], axis=1)

    def get_results(self, aggregated: bool = True) -> pd.DataFrame:
        if not aggregated:
            return self.results

        df = self.results

        if Status.ERROR.name in df.status.unique():
            logging.warning("The results contain errors which are filtered out for the final aggregation. "
                            "To see all results, call .get_results(aggregated=False)")
            df = df[df.status == Status.OK.name]

        keys = ["score", "preprocess_time", "main_time", "postprocess_time"]
        grouped_results = df.groupby(["algorithm", "collection", "dataset", "hyper_params_id"])
        repetitions = [len(v) for k, v in grouped_results.groups.items()]
        mean_results: pd.DataFrame = grouped_results.mean()[keys]
        std_results = grouped_results.std()[keys]
        results = mean_results.join(std_results, lsuffix="_mean", rsuffix="_std")
        results["repetitions"] = repetitions
        return results

    def save_results(self, results_path: Optional[Path] = None):
        path = results_path or (self.results_path / RESULTS_CSV)
        self.results.to_csv(path, index=False)

    def rsync_results(self):
        excluded_aliases = [
            hostname := socket.gethostname(),
            socket.gethostbyname(hostname),
            "localhost",
            socket.gethostbyname("localhost")
        ]

        hosts = self.remote_config.worker_hosts
        for host in hosts:
            if host not in excluded_aliases:
                subprocess.call(["rsync", "-a", f"{host}:{self.results_path}/", f"{self.results_path}"])

    def _prepare(self):
        for algorithm in self.exps.algorithms:
            algorithm.prepare()
        for exp in self.exps:
            exp.results_path.mkdir(parents=True, exist_ok=True)

    def _finalize(self):
        for algorithm in self.exps.algorithms:
            algorithm.finalize()

    def _distributed_prepare(self):
        tasks: List[Tuple[Callable, List, Dict]] = []
        for algorithm in self.exps.algorithms:
            if prepare_fn := algorithm.prepare_fn():
                tasks.append((prepare_fn, [], {}))
        for exp in self.exps:
            tasks.append((exp.results_path.mkdir, [], {"parents": True, "exist_ok": True}))
        self.remote.run_on_all_hosts(tasks)

    def _distributed_finalize(self):
        tasks: List[Tuple[Callable, List, Dict]] = []
        for algorithm in self.exps.algorithms:
            if finalize_fn := algorithm.finalize_fn():
                tasks.append((finalize_fn, [], {}))
        self.remote.run_on_all_hosts(tasks)
        self._resolve_future_results()
        self.remote.close()
        self.rsync_results()

    def run(self):
        assert len(self.exps.algorithms) > 0, "No algorithms given for evaluation"

        if self.distributed:
            self._distributed_prepare()
        else:
            self._prepare()

        self._run()

        if self.distributed:
            self._distributed_finalize()
        else:
            self._finalize()
        self.results.to_csv(self.results_path / RESULTS_CSV, index=False)

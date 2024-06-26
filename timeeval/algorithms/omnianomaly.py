# DO NOT EDIT THIS FILE!
# This file was automatically generated using the timeeval_experiments.generator from the template:
# timeeval_experiments/generator/templates/docker-algorithm.py.jinja
from durations import Duration
from typing import Any, Dict, Optional

from timeeval import Algorithm, TrainingType, InputDimensionality
from timeeval.adapters import DockerAdapter
from timeeval.params import ParameterConfig

import numpy as np


from timeeval.utils.window import ReverseWindowing
# post-processing for OmniAnomaly
def post_omni_anomaly(scores: np.ndarray, args: dict) -> np.ndarray:
    window_length = args.get("hyper_params", {}).get("window_size", 100)
    return ReverseWindowing(window_size=window_length).fit_transform(scores)


_omnianomaly_parameters: Dict[str, Dict[str, Any]] = {
 "batch_size": {
  "defaultValue": 50,
  "description": "Number of datapoints fitted parallel",
  "name": "batch_size",
  "type": "int"
 },
 "epochs": {
  "defaultValue": 10,
  "description": "Number of training passes over entire dataset",
  "name": "epochs",
  "type": "int"
 },
 "l2_reg": {
  "defaultValue": 0.0001,
  "description": "Regularization factor",
  "name": "l2_reg",
  "type": "float"
 },
 "latent_size": {
  "defaultValue": 3,
  "description": "Reduced dimension size",
  "name": "latent_size",
  "type": "int"
 },
 "learning_rate": {
  "defaultValue": 0.001,
  "description": "Learning Rate for Adam Optimizer",
  "name": "learning_rate",
  "type": "float"
 },
 "linear_hidden_size": {
  "defaultValue": 500,
  "description": "Dense layer size",
  "name": "linear_hidden_size",
  "type": "int"
 },
 "nf_layers": {
  "defaultValue": 20,
  "description": "NF layer size",
  "name": "nf_layers",
  "type": "int"
 },
 "random_state": {
  "defaultValue": 42,
  "description": "Seed for random number generation.",
  "name": "random_state",
  "type": "int"
 },
 "rnn_hidden_size": {
  "defaultValue": 500,
  "description": "Size of RNN hidden layer",
  "name": "rnn_hidden_size",
  "type": "int"
 },
 "split": {
  "defaultValue": 0.8,
  "description": "Train-validation split",
  "name": "split",
  "type": "float"
 },
 "window_size": {
  "defaultValue": 100,
  "description": "Sliding window size",
  "name": "window_size",
  "type": "int"
 }
}


def omnianomaly(params: Optional[ParameterConfig] = None, skip_pull: bool = False, timeout: Optional[Duration] = None) -> Algorithm:
    """OmniAnomaly

    Implementation of https://doi.org/10.1145/3292500.3330672


    **Algorithm Parameters:**

    latent_size: int
        Reduced dimension size (default: ``3``)
    rnn_hidden_size: int
        Size of RNN hidden layer (default: ``500``)
    window_size: int
        Sliding window size (default: ``100``)
    linear_hidden_size: int
        Dense layer size (default: ``500``)
    nf_layers: int
        NF layer size (default: ``20``)
    epochs: int
        Number of training passes over entire dataset (default: ``10``)
    split: float
        Train-validation split (default: ``0.8``)
    batch_size: int
        Number of datapoints fitted parallel (default: ``50``)
    l2_reg: float
        Regularization factor (default: ``0.0001``)
    learning_rate: float
        Learning Rate for Adam Optimizer (default: ``0.001``)
    random_state: int
        Seed for random number generation. (default: ``42``)

    Parameters
    ----------
    params : Optional[ParameterConfig]
        Parameter configuration for the algorithm
    skip_pull : bool
        Set to ``True`` to skip pulling the Docker image and use a local image instead.
        If the image is not present locally, this will raise an error.
    timeout : Optional[Duration]
        Set an individual execution and training timeout for this algorithm.
        This will overwrite the global timeouts set using :class:`~timeeval.ResourceConstraints`.

    Returns
    -------
    ~timeeval.Algorithm
        A correctly configured :class:`~timeeval.Algorithm` object for the OmniAnomaly algorithm.
    """
    return Algorithm(
        name="OmniAnomaly",
        main=DockerAdapter(
            image_name="ghcr.io/timeeval/omnianomaly",
            tag="0.3.0",
            skip_pull=skip_pull,
            timeout=timeout,
            group_privileges="akita",
        ),
        preprocess=None,
        postprocess=post_omni_anomaly,
        param_schema=_omnianomaly_parameters,
        param_config=params or ParameterConfig.defaults(),
        data_as_file=True,
        training_type=TrainingType.SEMI_SUPERVISED,
        input_dimensionality=InputDimensionality("multivariate")
    )

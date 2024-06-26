# DO NOT EDIT THIS FILE!
# This file was automatically generated using the timeeval_experiments.generator from the template:
# timeeval_experiments/generator/templates/docker-algorithm.py.jinja
from durations import Duration
from typing import Any, Dict, Optional

from timeeval import Algorithm, TrainingType, InputDimensionality
from timeeval.adapters import DockerAdapter
from timeeval.params import ParameterConfig


_ssa_parameters: Dict[str, Dict[str, Any]] = {
 "alpha": {
  "defaultValue": 0.2,
  "description": "Describes weights that are used for reference time series creation. Can be a single weight(float) or an array of weights. So far only supporting a single value",
  "name": "alpha",
  "type": "float"
 },
 "ep": {
  "defaultValue": 3,
  "description": "Score normalization value",
  "name": "ep",
  "type": "int"
 },
 "random_state": {
  "defaultValue": 42,
  "description": "Seed for random number generation.",
  "name": "random_state",
  "type": "int"
 },
 "rf_method": {
  "defaultValue": "alpha",
  "description": "`all`: Directly calculate reference timeseries from all points. `alpha`: Create weighted reference timeseries with help of parameter 'a'",
  "name": "rf_method",
  "type": "Enum[all,alpha]"
 },
 "window_size": {
  "defaultValue": 20,
  "description": "Size of sliding window.",
  "name": "window_size",
  "type": "int"
 }
}


def ssa(params: Optional[ParameterConfig] = None, skip_pull: bool = False, timeout: Optional[Duration] = None) -> Algorithm:
    """SSA

    Segmented Sequence Analysis calculates two piecewise linear models, aligns them and then computes the similarity between them. Finally a treshhold based approach is used to classify data as anomalous.

    .. warning::
       The implementation of this algorithm is not publicly available (closed source).
       Thus, TimeEval will fail to download the Docker image and the algorithm will not be available.
       Please contact the authors of the algorithm for the implementation and build the algorithm Docker image yourself.

    **Algorithm Parameters:**

    ep: int
        Score normalization value (default: ``3``)
    window_size: int
        Size of sliding window. (default: ``20``)
    rf_method: Enum[all,alpha]
        `all`: Directly calculate reference timeseries from all points. `alpha`: Create weighted reference timeseries with help of parameter 'a' (default: ``alpha``)
    alpha: float
        Describes weights that are used for reference time series creation. Can be a single weight(float) or an array of weights. So far only supporting a single value (default: ``0.2``)
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
        A correctly configured :class:`~timeeval.Algorithm` object for the SSA algorithm.
    """
    return Algorithm(
        name="SSA",
        main=DockerAdapter(
            image_name="ghcr.io/timeeval/ssa",
            tag="1.0.0",
            skip_pull=skip_pull,
            timeout=timeout,
            group_privileges="akita",
        ),
        preprocess=None,
        postprocess=None,
        param_schema=_ssa_parameters,
        param_config=params or ParameterConfig.defaults(),
        data_as_file=True,
        training_type=TrainingType.UNSUPERVISED,
        input_dimensionality=InputDimensionality("univariate")
    )

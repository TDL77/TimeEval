# DO NOT EDIT THIS FILE!
# This file was automatically generated using the timeeval_experiments.generator from the template:
# timeeval_experiments/generator/templates/docker-algorithm.py.jinja
from durations import Duration
from typing import Any, Dict, Optional

from timeeval import Algorithm, TrainingType, InputDimensionality
from timeeval.adapters import DockerAdapter
from timeeval.params import ParameterConfig


_if_lof_parameters: Dict[str, Dict[str, Any]] = {
 "alpha": {
  "defaultValue": 0.5,
  "description": "Scalar that depends on consideration of the dataset and controls the amount of data to be pruned",
  "name": "alpha",
  "type": "float"
 },
 "m": {
  "defaultValue": None,
  "description": "m features with highest scores will be used for pruning",
  "name": "m",
  "type": "int"
 },
 "max_samples": {
  "defaultValue": None,
  "description": "The number of samples to draw from X to train each tree: `max_samples * X.shape[0]`. If unspecified (`None`), then `max_samples=min(256, X.shape[0])`.",
  "name": "max_samples",
  "type": "float"
 },
 "n_neighbors": {
  "defaultValue": 10,
  "description": "Number neighbors to look at in local outlier factor calculation",
  "name": "n_neighbors",
  "type": "int"
 },
 "n_trees": {
  "defaultValue": 200,
  "description": "Number of trees in isolation forest",
  "name": "n_trees",
  "type": "int"
 },
 "random_state": {
  "defaultValue": 42,
  "description": "Seed for random number generation.",
  "name": "random_state",
  "type": "int"
 }
}


def if_lof(params: Optional[ParameterConfig] = None, skip_pull: bool = False, timeout: Optional[Duration] = None) -> Algorithm:
    """IF-LOF

    Isolation Forest - Local Outlier Factor: Uses a 3 step process - Building an isolation forest, pruning the forest with a computed treshhold, and applies local outlier factor to the resulting dataset


    **Algorithm Parameters:**

    n_trees: int
        Number of trees in isolation forest (default: ``200``)
    max_samples: float
        The number of samples to draw from X to train each tree: `max_samples * X.shape[0]`. If unspecified (`null`), then `max_samples=min(256, X.shape[0])`. (default: ``None``)
    n_neighbors: int
        Number neighbors to look at in local outlier factor calculation (default: ``10``)
    alpha: float
        Scalar that depends on consideration of the dataset and controls the amount of data to be pruned (default: ``0.5``)
    m: int
        m features with highest scores will be used for pruning (default: ``None``)
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
        A correctly configured :class:`~timeeval.Algorithm` object for the IF-LOF algorithm.
    """
    return Algorithm(
        name="IF-LOF",
        main=DockerAdapter(
            image_name="ghcr.io/timeeval/if_lof",
            tag="0.3.0",
            skip_pull=skip_pull,
            timeout=timeout,
            group_privileges="akita",
        ),
        preprocess=None,
        postprocess=None,
        param_schema=_if_lof_parameters,
        param_config=params or ParameterConfig.defaults(),
        data_as_file=True,
        training_type=TrainingType.UNSUPERVISED,
        input_dimensionality=InputDimensionality("multivariate")
    )

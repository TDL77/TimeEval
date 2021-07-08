from durations import Duration
from sklearn.model_selection import ParameterGrid
from typing import Any, Optional

from timeeval import Algorithm, TrainingType, InputDimensionality
from timeeval.adapters import DockerAdapter


_ssa_parameters = {
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


def ssa(params: Any = None, skip_pull: bool = False, timeout: Optional[Duration] = None) -> Algorithm:
    return Algorithm(
        name="SSA ",
        main=DockerAdapter(
            image_name="mut:5000/akita/ssa",
            skip_pull=skip_pull,
            timeout=timeout,
            group_privileges="akita",
        ),
        preprocess=None,
        postprocess=None,
        params=_ssa_parameters,
        param_grid=ParameterGrid(params or {}),
        data_as_file=True,
        training_type=TrainingType.UNSUPERVISED,
        input_dimensionality=InputDimensionality("univariate")
    )

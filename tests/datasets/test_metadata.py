import json
import tempfile
import unittest
from copy import copy
from pathlib import Path

import numpy as np

from timeeval.datasets.metadata import Trend, TrendType, DatasetMetadata, AnomalyLength, Stationarity, DatasetAnalyzer


class TestTrend(unittest.TestCase):
    def setUp(self) -> None:
        self.linear = Trend(
            tpe=TrendType.LINEAR,
            coef=0.78,
            confidence_r2=0.7
        )
        self.quadratic = Trend(
            tpe=TrendType.QUADRATIC,
            coef=2.8,
            confidence_r2=0.58
        )
        self.kubic = Trend(
            tpe=TrendType.KUBIC,
            coef=0.973,
            confidence_r2=0.6
        )

    def test_correct_name(self):
        self.assertEqual(self.linear.name, "linear trend")
        self.assertEqual(self.quadratic.name, "quadratic trend")
        self.assertEqual(self.kubic.name, "kubic trend")

    def test_correct_order(self):
        self.assertEqual(self.linear.order, 1)
        self.assertEqual(self.quadratic.order, 2)
        self.assertEqual(self.kubic.order, 3)

    def test_trend_type_from_order(self):
        self.assertEqual(self.linear.tpe, TrendType.from_order(1))
        self.assertEqual(self.quadratic.tpe, TrendType.from_order(2))
        self.assertEqual(self.kubic.tpe, TrendType.from_order(3))


class TestDatasetMetadata(unittest.TestCase):

    def setUp(self) -> None:
        self.base = DatasetMetadata(
            dataset_id=("test", "dataset1"),
            is_train=False,
            length=300,
            dimensions=2,
            contamination=0.01,
            num_anomalies=4,
            anomaly_length=AnomalyLength(min=7, median=10, max=12),
            means={},
            stddevs={},
            trends={},
            stationarities={},
        )

    def test_mean(self):
        meta = copy(self.base)
        meta.means = {
            "value1": 2.5,
            "value2": 4.0
        }
        self.assertEqual(self.base.mean, 0)
        self.assertEqual(meta.mean, np.mean([2.5, 4.0]))

    def test_stddev(self):
        meta = copy(self.base)
        meta.stddevs = {
            "value1": 1.45,
            "value2": 0.3
        }
        self.assertEqual(self.base.stddev, 0)
        self.assertEqual(meta.stddev, np.mean([1.45, 0.3]))

    def test_trend(self):
        meta = copy(self.base)
        meta.trends = {
            "value1": [],
            "value2": [Trend(TrendType.LINEAR, 1.78, 0.67), Trend(TrendType.QUADRATIC, 0.09, 0.54)],
            "value3": [Trend(TrendType.LINEAR, 5.4, 0.9)]
        }
        self.assertEqual(self.base.trend, "no trend")
        self.assertEqual(meta.trend, "quadratic trend")

    def test_stationarity(self):
        meta = copy(self.base)
        meta.stationarities = {
            "value1": Stationarity.TREND_STATIONARY,
            "value2": Stationarity.STATIONARY,
            "value3": Stationarity.DIFFERENCE_STATIONARY
        }
        self.assertEqual(self.base.stationarity, Stationarity.STATIONARY)
        self.assertEqual(self.base.get_stationarity_name(), "stationary")
        self.assertEqual(meta.stationarity, Stationarity.TREND_STATIONARY)
        self.assertEqual(meta.get_stationarity_name(), "trend_stationary")


class TestDatasetAnalyzer(unittest.TestCase):
    def setUp(self) -> None:
        self.dataset_path = Path("tests/example_data/dataset.train.csv")
        self.dataset_metadata = DatasetMetadata(
            dataset_id=('test', 'dataset1'),
            is_train=False,
            length=3600,
            dimensions=1,
            contamination=0.0002777777777777778,
            num_anomalies=1,
            anomaly_length=AnomalyLength(min=1, median=1, max=1),
            means={'value': 15836.711944444445},
            stddevs={'value': 7084.011043358856},
            trends={'value': []},
            stationarities={'value': Stationarity.DIFFERENCE_STATIONARY}
        )

    def test_wrong_arguments(self):
        with self.assertRaises(ValueError) as e:
            DatasetAnalyzer(("test", "dataset1"), is_train=False)
            self.assertIn("must be supplied", str(e))

    def test_analyzer_result(self):
        analyzer = DatasetAnalyzer(("test", "dataset1"), is_train=False, dataset_path=self.dataset_path)
        self.assertEqual(analyzer.metadata, self.dataset_metadata)

    def test_write_to_json(self):
        analyzer = DatasetAnalyzer(("test", "dataset1"), is_train=False, dataset_path=self.dataset_path)
        with tempfile.TemporaryDirectory() as tmp_path:
            tmp_path = Path(tmp_path)
            analyzer.save_to_json(tmp_path / "metadata.json")
            with open(tmp_path / "metadata.json", "r") as f:
                meta_json = json.load(f)
        self.assertDictEqual(meta_json, {
            "dataset_id": ["test", "dataset1"],
            "is_train": False,
            "length": 3600,
            "dimensions": 1,
            "contamination": 0.0002777777777777778,
            "num_anomalies": 1,
            "anomaly_length": {"min": 1, "median": 1, "max": 1},
            "means": {"value": 15836.711944444445},
            "stddevs": {"value": 7084.011043358856},
            "trends": {"value": []},
            "stationarities": {"value": "difference_stationary"}
        })

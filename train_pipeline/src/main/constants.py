from pathlib import Path

INPUT_DATA_BUCKET = "dummy-ml-model-input-data-bucket"
MODEL_STATS_BUCKET = "dummy-ml-pipeline-model-stats"

MODEL_DIR = Path("/opt/ml/model")
INPUT_DATA_DIR = Path("/opt/ml/input/data/train")
INPUT_DATA_NAME = "training_data_1.csv"
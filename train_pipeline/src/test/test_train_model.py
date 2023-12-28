import json
import os
from pathlib import Path

import boto3
import joblib
import pandas as pd
import pytest
from moto import mock_s3
from sklearn.linear_model import LinearRegression

from train_pipeline.src.main.train_model import (
    MODEL_DIR,
    MODEL_STATS_BUCKET,
    create_dummy_data,
    load_data_and_train,
)


def test_create_dummy_data():
    df = create_dummy_data()
    assert isinstance(df, pd.DataFrame), "The function should return a DataFrame"
    assert set(df.columns) == {"x1", "y"}, "DataFrame should have 'x1' and 'y' columns"
    assert len(df) == 100, "DataFrame should have 100 rows by default"

    df_seed = create_dummy_data(seed=1)
    df_seed_same = create_dummy_data(seed=1)
    pd.testing.assert_frame_equal(
        df_seed, df_seed_same, "DataFrames should be the same with the same seed"
    )


@mock_s3
def test_load_data_and_train_saves_to_s3(tmp_path):
    # Initialize the mock S3 environment
    conn = boto3.resource("s3", region_name="us-east-1")
    conn.create_bucket(Bucket=MODEL_STATS_BUCKET)

    # Prepare dummy data and call your function
    dummy_data = create_dummy_data()
    model_stats_key = "model/stats.json"
    load_data_and_train(dummy_data, model_stats_key, tmp_path)

    # Retrieve the object from S3 to verify
    s3_client = boto3.client("s3", region_name="us-east-1")
    obj = s3_client.get_object(Bucket=MODEL_STATS_BUCKET, Key=model_stats_key)
    metrics = json.loads(obj["Body"].read().decode("utf-8"))

    # Assertions to validate the data
    assert "r_2_train" in metrics, "r_2_train key should be in the metrics"


@mock_s3
def test_load_data_and_train(tmp_path):
    # Initialize the mock S3 environment
    conn = boto3.resource("s3", region_name="us-east-1")
    conn.create_bucket(Bucket=MODEL_STATS_BUCKET)

    load_data_and_train(create_dummy_data(), "test_prefix", tmp_path)

    # Check if the model file is created
    model_path = tmp_path / "model.joblib"
    assert model_path.exists(), "Model file should be created"

    # Load the model and check its type
    loaded_model = joblib.load(model_path)
    assert isinstance(
        loaded_model, LinearRegression
    ), "Loaded model should be a LinearRegression instance"

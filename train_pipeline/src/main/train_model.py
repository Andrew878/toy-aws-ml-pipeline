import argparse
import json
import os
from datetime import datetime
import boto3
from sklearn.linear_model import LinearRegression
import joblib
from pathlib import Path
import pandas as pd
import numpy as np

from train_pipeline.src.main.constants import MODEL_DIR, MODEL_STATS_BUCKET, INPUT_DATA_DIR, INPUT_DATA_NAME


def create_dummy_data(n_samples:int = 100, seed:int=0)->pd.DataFrame:

    # Numeric columns
    np.random.seed(seed)
    x1 = np.array(range(0,100))
    y = x1*5 + np.random.randn(n_samples)

    # Creating the DataFrame
    return pd.DataFrame({
        'x1': x1,
        'y': y,
    })


def load_data_and_train(train_data:pd.DataFrame,model_stats_key:str, model_dir:Path = MODEL_DIR)->None:

    X_train = train_data.drop('y', axis=1)
    y_train = train_data['y']
    # Train the model
    model = LinearRegression()
    model.fit(X_train, y_train)
    # Save the model to the /opt/ml/model directory
    model_dir.mkdir(exist_ok=True, parents=True)
    joblib.dump(model, os.path.join(model_dir, 'model.joblib'))

    metrics = {
        "r_2_train": model.score(X_train, y_train)}

    # Convert metrics to JSON string
    metrics_json = json.dumps(metrics)

    # Define S3 path (make sure the bucket and key are unique and have write permissions)
    s3 = boto3.client('s3')

    # Upload the JSON string to S3
    s3.put_object(Bucket=MODEL_STATS_BUCKET, Key=model_stats_key, Body=metrics_json)


if __name__ =='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_stats_key', type=str)
    args = parser.parse_args()
    # Now you can use args.current_datetime in your script
    model_stats_key = args.model_stats_key
    load_data_and_train(train_data = pd.read_csv(INPUT_DATA_DIR / INPUT_DATA_NAME),model_stats_key=model_stats_key)

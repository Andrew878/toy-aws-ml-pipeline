import datetime

import sagemaker
from sagemaker.inputs import TrainingInput
from sagemaker.model_metrics import MetricsSource, ModelMetrics
from sagemaker.sklearn.estimator import SKLearn
from sagemaker.workflow.parameters import ParameterString
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.step_collections import RegisterModel
from sagemaker.workflow.steps import TrainingStep

from train_pipeline.src.main.constants import (INPUT_DATA_BUCKET,
                                               INPUT_DATA_NAME,
                                               MODEL_STATS_BUCKET)

# Initialize the SageMaker session and role
sagemaker_session = sagemaker.Session()
role = sagemaker.get_execution_role()
sess = sagemaker.Session()
DEFAULT_SM_BUCKET = sess.default_bucket()  # Set a default S3 bucket


# Current datetime as a string
current_datetime = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
model_stats_key = f"{current_datetime}/model-statistics.json"


# Define parameters for pipeline execution
input_data = ParameterString(
    name="InputData", default_value=f"s3://{DEFAULT_SM_BUCKET}/{INPUT_DATA_NAME}"
)
_INSTANCE_TYPE = "ml.m4.xlarge"

# Define a SKLearn estimator for model training
estimator = SKLearn(
    entry_point="train_model.py",
    role=role,
    instance_count=1,
    instance_type=_INSTANCE_TYPE,
    framework_version="0.23-1",
    base_job_name="sklearn-train-job",
    sagemaker_session=sagemaker_session,
    hyperparameters={"model_stats_key": model_stats_key},
)

# Define the training step
training_step = TrainingStep(
    name="TrainModel",
    estimator=estimator,
    inputs={"train": TrainingInput(s3_data=input_data, content_type="text/csv")},
)

# Define model metrics for model registration
model_metrics = ModelMetrics(
    model_statistics=MetricsSource(
        s3_uri=f"s3://{DEFAULT_SM_BUCKET}/{model_stats_key}",
        content_type="application/json",
    )
)

# Define the model registration step
register_model = RegisterModel(
    name="RegisterModel",
    estimator=estimator,
    model_data=training_step.properties.ModelArtifacts.S3ModelArtifacts,
    content_types=["application/json"],
    response_types=["application/json"],
    inference_instances=[_INSTANCE_TYPE],
    transform_instances=[_INSTANCE_TYPE],
    model_package_group_name="dummy-ml-pipeline-model-group",
    model_metrics=model_metrics,
)

# Define the SageMaker Pipeline
pipeline = Pipeline(
    name="MySamplePipeline",
    parameters=[input_data],
    steps=[training_step, register_model],
    sagemaker_session=sagemaker_session,
)

# Create (or update) the pipeline
pipeline.upsert(role_arn=role)

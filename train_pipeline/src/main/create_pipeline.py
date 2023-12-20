import sagemaker
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.step_collections import RegisterModel
from sagemaker.workflow.steps import TrainingStep
from sagemaker.workflow.parameters import ParameterString
from sagemaker.sklearn.estimator import SKLearn
from sagemaker.model_metrics import MetricsSource, ModelMetrics
from sagemaker.inputs import TrainingInput
import datetime

from train_pipeline.src.main.constants import MODEL_STATS_BUCKET, INPUT_DATA_BUCKET, INPUT_DATA_NAME

# Initialize the SageMaker session and role
sagemaker_session = sagemaker.Session()
role = sagemaker.get_execution_role()

# Current datetime as a string
current_datetime = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
model_stats_key = f"{current_datetime}/model-statistics.json"


# Define parameters for pipeline execution
input_data = ParameterString(
    name="InputData",
    default_value=f"s3://{INPUT_DATA_BUCKET}/{INPUT_DATA_NAME}/"
)

# Define a SKLearn estimator for model training
estimator = SKLearn(
    entry_point='train.py',
    role=role,
    instance_count=1,
    instance_type='ml.m5.large',
    framework_version='0.23-1',
    base_job_name='sklearn-train-job',
    sagemaker_session=sagemaker_session,
    hyperparameters={
        'model_stats_key': model_stats_key}
)

# Define the training step
training_step = TrainingStep(
    name="TrainModel",
    estimator=estimator,
    inputs={
        "train": TrainingInput(
            s3_data=input_data,
            content_type="text/csv"
        )
    }
)

# Define model metrics for model registration
model_metrics = ModelMetrics(
    model_statistics=MetricsSource(
        s3_uri=f"s3://{MODEL_STATS_BUCKET}/{model_stats_key}",
        content_type="application/json"
    )
)

# Define the model registration step
register_model = RegisterModel(
    name="RegisterModel",
    estimator=estimator,
    model_data=training_step.properties.ModelArtifacts.S3ModelArtifacts,
    content_types=["application/json"],
    response_types=["application/json"],
    inference_instances=["ml.t2.medium", "ml.m5.large"],
    transform_instances=["ml.m5.large"],
    model_package_group_name="YourModelPackageGroupName",
    model_metrics=model_metrics
)

# Define the SageMaker Pipeline
pipeline = Pipeline(
    name='MySamplePipeline',
    parameters=[input_data],
    steps=[training_step, register_model],
    sagemaker_session=sagemaker_session
)

# Create (or update) the pipeline
pipeline.upsert(role_arn=role)

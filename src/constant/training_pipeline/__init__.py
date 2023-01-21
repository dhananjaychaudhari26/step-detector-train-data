import os

SAVED_MODEL_DIR =os.path.join("saved_models")
# defining common constant variable for training pipeline
PIPELINE_NAME: str = "stepDetector"
S3_BUCKET_NAME:str = "ms-search-engine"
NEW_DATA_PATH:str = "upload/data"
NEW_DATA_DIR:str = "data_validation"
ARTIFACT_DIR: str = "artifact"
LOGS_DIR: str = "logs"
FILE_NAME: str = "data.csv"
PREV_DATA_DIR_NAME = "trained"
TRAIN_FILE_NAME: str = "train.csv"
TEST_FILE_NAME: str = "test.csv"
PREPROCSSING_OBJECT_FILE_NAME = "preprocessing.pkl"
MODEL_FILE_NAME = "model.h5"
ANDROID_FILE_NAME = "android.tflite"
IOS_FILE_NAME = "ios.mlmodel"
BASE_URL = "https://pdapiv2.projectdasein.com"
UPDATE_INTERVAL_NOTES_URI = "api/mlmodel/upload"
VERSION_TXT_FILE = "version.txt"
NUMBER_OF_FEATURES = 40

"""
Data Ingestion related constant start with DATA_INGESTION VAR NAME
"""
# DATA_INGESTION_COLLECTION_NAME: str = "sensor"
DATA_INGESTION_DIR_NAME: str = "data_ingestion"
DATA_INGESTION_FEATURE_STORE_DIR: str = "feature_store"
DATA_INGESTION_INGESTED_DIR: str = "ingested"
DATA_INGESTION_TRAIN_TEST_SPLIT_RATION: float = 0.2
"""
Model Trainer ralated constant start with MODE TRAINER VAR NAME
"""

MODEL_TRAINER_DIR_NAME: str = "model_trainer"
MODEL_TRAINER_TRAINED_MODEL_DIR: str = "trained_model"
# MODEL_TRAINER_TRAINED_MODEL_NAME: str = "model.pkl"


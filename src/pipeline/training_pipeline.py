from src.entity.config_entity import TrainingPipelineConfig, DataIngestionConfig,ModelTrainerConfig
from src.entity.artifact_entity import DataIngestionArtifact,ModelTrainerArtifact
from src.exception import StepException
import sys,os
from src.logger import logging
from src.components.data_ingestion import DataIngestion
from src.components.model_trainer import ModelTrainer
from src.cloud.s3_syncer import S3Connection
from src.constant  import training_pipeline
import shutil
# s3_connection = S3Connection()
class TrainPipeline:
    def __init__(self):
        self.training_pipeline_config = TrainingPipelineConfig()
        self.s3_sync = S3Connection()
        

    def start_data_ingestion(self)->DataIngestionArtifact:
        try:
            self.data_ingestion_config = DataIngestionConfig(training_pipeline_config=self.training_pipeline_config)
            logging.info("Starting data ingestion")
            data_ingestion = DataIngestion(data_ingestion_config=self.data_ingestion_config)
            data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
            logging.info(f"Data ingestion completed and artifact: {data_ingestion_artifact}")
            return data_ingestion_artifact
        except  Exception as e:
            raise  StepException(e,sys)

    
    def start_model_trainer(self,data_ingestion_artifact:DataIngestionArtifact)->ModelTrainerArtifact:
        try:
            model_trainer_config = ModelTrainerConfig(training_pipeline_config=self.training_pipeline_config)
            model_trainer = ModelTrainer(model_trainer_config, data_ingestion_artifact)
            model_trainer_artifact = model_trainer.initiate_model_trainer()
            return model_trainer_artifact
        except  Exception as e:
            logging.error(f"{e}")
            raise StepException(e,sys)


    def run_pipeline(self):
        try:
            self.s3_sync.sych_artifact_from_s3(training_pipeline_config=self.training_pipeline_config)
            data_ingestion_artifact:DataIngestionArtifact = self.start_data_ingestion()
            model_trainer_artifact = self.start_model_trainer(data_ingestion_artifact)
            self.s3_sync.sync_artifact_to_s3(training_pipeline_config=self.training_pipeline_config)

            # delete all local directories
            try:
                shutil.rmtree(training_pipeline.ARTIFACT_DIR)
                shutil.rmtree(training_pipeline.NEW_DATA_DIR)
                # shutil.rmtree(training_pipeline.LOGS_DIR)
                shutil.rmtree(training_pipeline.PREV_DATA_DIR_NAME)
            except Exception as e:
                raise  StepException(e,sys)

             #sync latest logs to s3
            s3_logs_path = f"s3://{self.s3_sync.bucket}/{training_pipeline.LOGS_DIR}/{self.training_pipeline_config.timestamp}.log"
            self.s3_sync.sync_folder_to_s3(os.path.join(training_pipeline.LOGS_DIR,self.training_pipeline_config.timestamp+".log"),s3_logs_path)
        except  Exception as e:
            raise StepException(e,sys)

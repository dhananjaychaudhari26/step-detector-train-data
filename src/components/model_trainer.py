
# from sensor.utils.main_utils import load_numpy_array_data
from src.exception import StepException
from src.logger import logging
from src.entity.artifact_entity import DataIngestionArtifact,ModelTrainerArtifact
from src.entity.config_entity import ModelTrainerConfig
import os,sys
import pandas as pd
from  src.ml.architecture.architecture import StepModel
from src.cloud.s3_syncer import S3Connection
from src.utils.network import Network
from src.constant.training_pipeline import UPDATE_INTERVAL_NOTES_URI

class ModelTrainer:

    def __init__(self,model_trainer_config:ModelTrainerConfig,
        data_ingestion_artifact:DataIngestionArtifact):
        try:
            self.model_trainer_config=model_trainer_config
            self.data_ingestion_artifact=data_ingestion_artifact
            self.model = StepModel()
        except Exception as e:
            raise StepException(e,sys)


    
    def initiate_model_trainer(self)->ModelTrainerArtifact:
        try:
            logging.info(f"Start Model training:")
            #loading training array and testing array
            train_data = pd.read_csv(self.data_ingestion_artifact.trained_file_path)
            test_data = pd.read_csv(self.data_ingestion_artifact.test_file_path)

            train_data.replace(["left","right"],[0,1], inplace=True)
            test_data.replace(["left","right"],[0,1], inplace=True)
            
            X_train, y_train, X_test, y_test = (
                train_data.iloc[:, :-1],
                train_data.iloc[:, -1],
                test_data.iloc[:, :-1],
                test_data.iloc[:, -1],
            )
            logging.info(f"X_Train shape {X_train.shape}, X_test shape {X_test.shape}")
            self.model.create_model()
            self.model.compile()
            history = self.model.fit(X_train,X_test,y_train,y_test)
            model_dir_path = os.path.dirname(self.model_trainer_config.trained_model_file_path)
            os.makedirs(model_dir_path,exist_ok=True)
            self.model.save_model(self.model_trainer_config.trained_model_file_path)

            #send model details to server
            # s3_connection.create_s3_url(self.model_trainer_config.trained_model_file_path)
            # response = network.make_post_call(path=UPDATE_INTERVAL_NOTES_URI,body=request_body)
            #model trainer artifact
            model_trainer_artifact = ModelTrainerArtifact(trained_model_file_path=self.model_trainer_config.trained_model_file_path)
            logging.info(f"Model trainer artifact: {model_trainer_artifact}")
            # return model_trainer_artifact
        except Exception as e:
            logging.error(f"{e}")
            raise StepException(e,sys)
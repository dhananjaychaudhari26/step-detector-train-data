from src.exception import StepException
from src.logger import logging
from src.entity.config_entity import DataIngestionConfig
from src.entity.artifact_entity import DataIngestionArtifact
from sklearn.model_selection import train_test_split
import os,sys
from pandas import DataFrame
import pandas as pd
from src.cloud.s3_syncer import S3Connection
from src.constant  import training_pipeline
# from src.data_access.sensor_data import SensorData
# from sensor.utils.main_utils import read_yaml_file
# from sensor.constant.training_pipeline import SCHEMA_FILE_PATH
class DataIngestion:

    def __init__(self,data_ingestion_config:DataIngestionConfig):
        try:
            self.data_ingestion_config=data_ingestion_config
            self.s3_sync = S3Connection()
        except Exception as e:
            raise StepException(e,sys)
        
    def export_data_into_feature_store(self) -> DataFrame:
        """
        Export mongo db collection record as data frame into feature
        """
        try:
            logging.info("Download new data from s3 and merger with existing train data")
            try:     
                data = pd.read_csv(os.path.join(self.data_ingestion_config.previous_data_dir,training_pipeline.FILE_NAME))
            except:
                features= []
                for i in range(training_pipeline.NUMBER_OF_FEATURES):
                    features.append(f"feature_{i}")
                features.append("label")
                data = pd.DataFrame(columns=features)
                
            logging.info(f"Existing data with shape {data.shape}")  

            for csv in os.listdir(self.data_ingestion_config.new_data_dir):
                df= pd.read_csv(os.path.join(self.data_ingestion_config.new_data_dir, csv))
                df = df[df["label"].isin(["left","right"])]
                data = data.append(df)

            logging.info(f"Merged data with shape before drop duplicate {data.shape}")  
            logging.info(f"Dropping duplicates")

            features= []
            for i in range(training_pipeline.NUMBER_OF_FEATURES):
                features.append(f"feature_{i}")
            data.drop_duplicates(subset=features,inplace=True)
            logging.info(f"Merged data with shape after drop duplicate {data.shape}")  
            data.to_csv(os.path.join(self.data_ingestion_config.previous_data_dir,training_pipeline.FILE_NAME), index=False)
            
            feature_store_file_path = self.data_ingestion_config.feature_store_file_path 

            #creating folder
            logging.info(f"Exporting feature store.")
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path,exist_ok=True)
            data.to_csv(feature_store_file_path,index=False,header=True)
            return data
        except  Exception as e:
            logging.error(f"{e}")
            raise  StepException(e,sys)
    
    def split_data_as_train_test(self, dataframe: DataFrame) -> None:
        """
        Feature store dataset will be split into train and test file
        """

        try:
            train_set, test_set = train_test_split(
                dataframe, test_size=self.data_ingestion_config.train_test_split_ratio
            )

            logging.info("Performed train test split on the dataframe")

            logging.info(
                "Exited split_data_as_train_test method of Data_Ingestion class"
            )

            dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)

            os.makedirs(dir_path, exist_ok=True)

            logging.info(f"Exporting train and test file path.")

            train_set.to_csv(
                self.data_ingestion_config.training_file_path, index=False, header=True
            )

            test_set.to_csv(
                self.data_ingestion_config.testing_file_path, index=False, header=True
            )

            logging.info(f"Exported train and test file path.")
        except Exception as e:
            logging.error(f"{e}")
            raise StepException(e,sys)
    

    def initiate_data_ingestion(self) -> DataIngestionArtifact:
        try:
            dataframe = self.export_data_into_feature_store()
            self.split_data_as_train_test(dataframe=dataframe)
            data_ingestion_artifact = DataIngestionArtifact(trained_file_path=self.data_ingestion_config.training_file_path,
            test_file_path=self.data_ingestion_config.testing_file_path)
            return data_ingestion_artifact
        except Exception as e:
            raise StepException(e,sys)
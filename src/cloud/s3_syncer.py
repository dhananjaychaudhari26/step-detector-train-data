import os,sys
import boto3
from dotenv import load_dotenv
from src.constant  import training_pipeline
from src.exception import StepException
from src.logger import logging
from src.utils.network import Network
load_dotenv()
network = Network()
import shutil
# https://ms-search-engine.s3.ap-south-1.amazonaws.com/artifact/01_19_2023_14_55_29/model_trainer/trained_model/android.tflite

class S3Connection:
    def __init__(self):
        session = boto3.Session(
            aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        )
        self.s3_client = session.client("s3")
        self.bucket = os.environ["AWS_BUCKET_NAME"]
        self.region = os.environ["AWS_REGION"]

    def sync_folder_to_s3(self,folder,aws_buket_url):
        command = f"aws s3 sync {folder} {aws_buket_url} "
        print("command: ", command)
        os.system(command)

    def sync_folder_from_s3(self,folder,aws_bucket_url):
        command = f"aws s3 sync  {aws_bucket_url} {folder} "
        os.system(command)

    def download_from_s3(self,path):
        try:
            print("PATH: ",path)
            self.s3_client.download_file(Bucket=self.bucket, Key=path, Filename=path)
        except Exception as e:
            logging.error(f"{e}")
            raise StepException(e, sys)

    def sych_artifact_from_s3(self,training_pipeline_config):
        logging.info(f"Synching artifact, data validation and data from s3")
        logging.info(f"Creating empty directory")
        if not os.path.exists(training_pipeline.ARTIFACT_DIR):
            os.makedirs(training_pipeline.ARTIFACT_DIR)

        if not os.path.exists(training_pipeline.PREV_DATA_DIR_NAME):
            os.makedirs(training_pipeline.PREV_DATA_DIR_NAME)    
        
        try:
            #download artifact version file
            self.download_from_s3(f"{training_pipeline.ARTIFACT_DIR}/{training_pipeline.VERSION_TXT_FILE}")
            #download previous data file
            self.download_from_s3(f"{training_pipeline.PREV_DATA_DIR_NAME}/{training_pipeline.FILE_NAME}")
        except:
            pass    
       
        #sync all files from data_validation folder
        s3_data_validation_path = f"s3://{self.bucket}/{training_pipeline.NEW_DATA_PATH}/{training_pipeline.NEW_DATA_DIR}"
        # print(s3_data_validation_path)
        self.sync_folder_from_s3(training_pipeline.NEW_DATA_DIR,s3_data_validation_path)

    def upload_to_s3(self, path,file_name):
        try:
            self.s3_client.upload_file(
                Filename = f"{path}/{file_name}",
                Bucket = self.bucket,
                Key= f"{path}/{file_name}",
            )
        except Exception as e:
            logging.error(f"{e}")
            raise StepException(e,sys)

    def sync_artifact_to_s3(self,training_pipeline_config):
        try:
            #Sync latest artifact to s3
            s3_artifact_path = f"s3://{self.bucket}/{training_pipeline.ARTIFACT_DIR}/{training_pipeline_config.timestamp}"
            self.sync_folder_to_s3(os.path.join(training_pipeline.ARTIFACT_DIR,training_pipeline_config.timestamp),s3_artifact_path)
            #upload model file to artifact dir 
            # self.upload_to_s3(training_pipeline.PREV_DATA_DIR_NAME, training_pipeline.FILE_NAME)
            self.s3_client.upload_file(
                Filename = f"{training_pipeline.ARTIFACT_DIR}/{training_pipeline_config.timestamp}/{training_pipeline.MODEL_TRAINER_DIR_NAME}/{training_pipeline.MODEL_TRAINER_TRAINED_MODEL_DIR}/{training_pipeline.MODEL_FILE_NAME}",
                Bucket = self.bucket,
                Key= f"{training_pipeline.ARTIFACT_DIR}/{training_pipeline.ARTIFACT_MODEL_PATH}/{training_pipeline.MODEL_FILE_NAME}",
            )
            #upload trained/data.csv file to s3
            # self.upload_to_s3(training_pipeline.PREV_DATA_DIR_NAME, training_pipeline.FILE_NAME)

            # Delete all csv files from s3 present in data_validation folder after training
            # response = self.s3_client.list_objects(Bucket=self.bucket, Prefix=f"{training_pipeline.NEW_DATA_PATH}/{training_pipeline.NEW_DATA_DIR}", MaxKeys=1000)
            # if 'Contents' in response:
            #     for object in response['Contents']:
            #         self.s3_client.delete_object(Bucket=self.bucket, Key=object['Key'])

            #Call Service to update model details to server
            # https://ms-search-engine.s3.ap-south-1.amazonaws.com/artifact/01_20_2023_23_08_30/model_trainer/trained_model/android.tflite
            common_url = f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{training_pipeline.ARTIFACT_DIR}/{training_pipeline_config.timestamp}/{training_pipeline.MODEL_TRAINER_DIR_NAME}/{training_pipeline.MODEL_TRAINER_TRAINED_MODEL_DIR}"
            
            version = 1.0
            try:
                f = open(f"{training_pipeline.ARTIFACT_DIR}/{training_pipeline.VERSION_TXT_FILE}", "r")
                for x in f:
                    version = float(x)+1
                f.close()    
            except:
                version = 1.0

            request_body = {
                "ml_model": f"{common_url}/{training_pipeline.MODEL_FILE_NAME}",
                "android_ml_model": f"{common_url}/{training_pipeline.ANDROID_FILE_NAME}",
                "ios_ml_model": f"{common_url}/{training_pipeline.IOS_FILE_NAME}",
                "version": f"v{version}"
            }
            logging.info(f"{request_body}")
            response = network.make_post_call(path=training_pipeline.UPDATE_INTERVAL_NOTES_URI, body=request_body)
            logging.info(f"{response}")

            with open(f"{training_pipeline.ARTIFACT_DIR}/{training_pipeline.VERSION_TXT_FILE}", 'w') as f:
                f.write(str(version))

            #upload version text file to s3
            self.upload_to_s3(training_pipeline.ARTIFACT_DIR, training_pipeline.VERSION_TXT_FILE)

            # delete all local directories
            # shutil.rmtree(training_pipeline.ARTIFACT_DIR)
            # shutil.rmtree(training_pipeline.NEW_DATA_DIR)
            # shutil.rmtree(training_pipeline.LOGS_DIR)
            # shutil.rmtree(training_pipeline.PREV_DATA_DIR_NAME)

        except Exception as e:
            logging.error(f"{e}")
            raise StepException(e,sys)




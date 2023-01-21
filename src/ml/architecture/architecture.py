# from sensor.constant.training_pipeline import SAVED_MODEL_DIR,MODEL_FILE_NAME
import os,sys
import tensorflow as tf
from tensorflow.keras import Sequential
from src.exception import StepException
from tensorflow.keras.layers import Dense, Input, Flatten, Conv2D, MaxPool2D
from src.constant.training_pipeline import MODEL_FILE_NAME,ANDROID_FILE_NAME,IOS_FILE_NAME
import coremltools as ct
from src.logger import logging
class StepModel:

    def __init__(self):
        try:
            self.model = None
        except Exception as e:
            raise e
    
    def create_model(self)->None:
        self.model = Sequential([
          Input(shape=40),
          Dense(units=128, activation="relu"),
          Dense(units=64, activation="relu"),
          Dense(units=32, activation="relu"),
          Dense(units=32, activation="relu"),
          Dense(units=2, activation="softmax"),
      ])

    def compile(self)->None:
        self.model.compile(optimizer="adam", loss=tf.keras.losses.SparseCategoricalCrossentropy(), metrics="acc") 
    
    def fit(self, X_train,X_test,y_train,y_test):
        history = self.model.fit(x=X_train, y=y_train, batch_size=256, epochs=10, validation_data=(X_test, y_test))
        return history

    def save_model(self, path_:str) ->None:
        try:
            ## SAVE RAW MODEL
            self.model.save(os.path.join(path_,MODEL_FILE_NAME))

            ## SAVE ANDROID MODEL 
            model_v2 = tf.keras.models.load_model(os.path.join(path_,MODEL_FILE_NAME))
            tflite_v2 = tf.lite.TFLiteConverter.from_keras_model(model_v2)
            android_model_v2 = tflite_v2.convert()
            with open(os.path.join(path_,ANDROID_FILE_NAME),'wb') as f:
                f.write(android_model_v2)
            #SAVE IOS MODEL
            coreml_v2 = ct.convert(model_v2)
            coreml_v2.save(os.path.join(path_,IOS_FILE_NAME))
        except Exception as e:
            logging.error(f"{e}")
            raise StepException(e,sys)   






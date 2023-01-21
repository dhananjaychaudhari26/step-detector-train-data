from  src.constant.training_pipeline import BASE_URL
import requests
import json
class Network:
    def __init__(self) -> None:
        self.base_url = BASE_URL

    def make_post_call(self,path:str,body:dict={})->dict():
        url = self.base_url +"/"+path
        print("Url: ", url)
        print("Request body: ", body)
        try:
            response = requests.post(url, json = body)
            response = json.loads(response.text)
            return response
        except Exception as e:
            return {"code": 500,
                "status": "fail",
                "message": "Exception: "+ e}  
        
import requests
# from service_interface import ServiceInterface
from PIL import Image
from typing import List
import numpy as np
import json
import os

class SummyService():
    def __init__(self):
        # self.summy_service_ip = 'http://74.82.29.209:8010/infer'#'http://184.105.3.17:8086/infer'
        self.summy_service_ip = 'http://127.0.0.1:8010/infer'#'http://184.105.3.17:8086/infer'
        self.headers = {
            'accept': '*/*'
        }
    
    def get_response(self, movie_id, frame_boundary=[], caption_type='vlm', append_to_db=False):#HK @TODO
        
        print("Working on movie_id: {}".format(movie_id))
        files = {
            'movie_id': (None, movie_id),
            'frame_boundary': (None, str(frame_boundary)), 
            'caption_type': (None, caption_type),
            'append_to_db' :(None, append_to_db)
        }
        try:
            response = requests.post(self.summy_service_ip, headers=self.headers, files=files)
            return [response.json()['answer']]
        except Exception as e:
            print("Error: {}".format(e))
            return None

def main():
    # os.environ["GEVENT_SUPPORT"]="1"
    summy_service = SummyService() # run that for debug
    
    movie_id = "Movies/7417592353856606351"
    if 1:
        outputs = summy_service.get_response(movie_id,[[5, 476], [494, 800]], 'vlm', 1)
        # outputs = summy_service.get_response(movie_id,[[5, 476]], 'vlm')
    else:
        outputs = summy_service.get_response(movie_id)

    print("Outputs: {}".format(outputs))

if __name__ == "__main__":
    main()
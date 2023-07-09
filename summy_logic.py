from gevent import monkey
monkey.patch_all()
import tritonclient.http as httpclient
from PIL import Image
import requests
import numpy as np
import time
import os
from arango import ArangoClient
from database.arangodb import NEBULA_DB

class SceneSummyLogic():
    def __init__(self):
        self.dbname = "ipc_200"
        self.arango_host = "http://172.83.9.249:8010"
        self.client = ArangoClient(hosts=self.arango_host)
        self.db = self.client.db(self.dbname, username='nebula', password='nebula')
        self.nre = NEBULA_DB()


    def get_movie_structure(self, movie_id):
        try:
            movie_structure = self.nre.get_doc_by_key({'_id': movie_id}, "Movies")
            return movie_structure
        except Exception as e:
            print(e) 
            return None


def main(): 

    scene_summy_service = SceneSummyLogic()
    os.environ["GEVENT_SUPPORT"]="1"
    movie_id = "Movies/7417592353856606351"
    movie_id = "Movies/7417592353856606351"

    outputs = scene_summy_service.get_movie_structure(movie_id,[[5, 476], [494, 800]], 'blip2', 0)


    print("Outputs: {}".format(outputs))

if __name__ == "__main__":
    main()
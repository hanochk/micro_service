from gevent import monkey
monkey.patch_all()
import tritonclient.http as httpclient
from PIL import Image
import requests
import numpy as np
import time

from arango import ArangoClient
from database.arangodb import NEBULA_DB

class SceneSummyLogic():
    def __init__(self):
        self.dbname = "ipc_200"
        self.arango_host = "http://172.83.9.249:8529"
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

    movie_id = "Movies/-4092337253497764854"
    
    outputs = scene_summy_service.get_movie_structure(movie_id)

    print("Outputs: {}".format(outputs))

if __name__ == "__main__":
    main()
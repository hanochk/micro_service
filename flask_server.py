import json
import mimetypes
import os
from io import BytesIO
from urllib.parse import urlparse

import requests
from PIL import Image
from flask import Flask, request, jsonify, send_file
from flask import make_response
from flask_cors import CORS
from flask_siwadoc import SiwaDoc
# from obs import ObsClient
from pydantic import BaseModel
# from werkzeug.utils import secure_filename
# from triton_util import infer_from_image
from summy_logic import SceneSummyLogic

# The web page server. It receives requests from front end and send request to triton backend.

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
# CORS(app)  # enable CORS

siwa = SiwaDoc(app, title="VQA demo doc")

# Define the allowed file extensions
ALLOWED_EXTENSIONS = {'jpg', 'png', 'txt', 'jpeg'}

summy_service = SceneSummyLogic()

# # load config json
# with open('config.json') as f:
#     # Load the JSON data into a Python dictionary
#     data = json.load(f)

# AK = data["ak"]
# SK = data["sk"]
# OBS_ENDPOINT = data["endpoint"]
# OBS_WORK_BUCKET_NAME = 'digital-human-video'
# OBS_WORK_FOLDER = 'vid-arts-storage'


# Helper function to check if a file extension is allowed
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_error(resp):
    if resp.status > 300:
        return {
            'errorCode': resp.errorCode,
            'errorMessage': resp.errorMessage
        }
    return None


# response.headers.add('Access-Control-Allow-Origin', 'http://124.70.217.159:8080')
# add this after_request decorator to all routes
# @app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept,X-requested-with')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


# Handle file upload requests
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        print("No file uploaded")
        return make_response(jsonify(error='No file uploaded'), 400)

    file = request.files['file']

    if file.filename == '':
        print("No file selected")
        return make_response(jsonify(error='No file selected'), 400)

    if not allowed_file(file.filename):
        print("Invalid file type")
        return make_response(jsonify(error='Invalid file type'), 400)

    upload_folder = 'uploads'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    filename = file.filename#secure_filename(file.filename)

    # upload to obs
    obsClient = ObsClient(access_key_id=AK, secret_access_key=SK, server=OBS_ENDPOINT)
    resp = obsClient.putContent(OBS_WORK_BUCKET_NAME, f"{OBS_WORK_FOLDER}/{filename}", file)
    if err := get_error(resp):
        return make_response(jsonify(err), 400)

    response = make_response(jsonify(message='File uploaded successfully'), 200)

    return response


@app.route('/query', methods=['POST'])
def get_uploaded_files():
    # list obs files
    obsClient = ObsClient(access_key_id=AK, secret_access_key=SK, server=OBS_ENDPOINT)
    resp = obsClient.listObjects(OBS_WORK_BUCKET_NAME, OBS_WORK_FOLDER)
    if err := get_error(resp):
        return make_response(jsonify(err), 400)
    files = [content.key for content in resp.body.contents if not content.key.endswith("/")]

    response = jsonify(files=files)
    # response.headers.add('Content-Type', 'application/json')
    # if not response.headers.get('Access-Control-Allow-Origin'):
    #     response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@app.route('/download/<path:filename>', methods=['GET'])
def download_image(filename):
    if not filename.startswith(OBS_WORK_FOLDER):
        return make_response(jsonify(error='wrong folder!'), 400)

    # download the image
    obsClient = ObsClient(access_key_id=AK, secret_access_key=SK, server=OBS_ENDPOINT)
    resp = obsClient.getObject(OBS_WORK_BUCKET_NAME, filename)
    if err := get_error(resp):
        return make_response(jsonify(err), 400)

    # response to PILImage
    response = resp.body.response
    img = Image.open(BytesIO(response.read()))

    mime_type = filename.split(".")[-1]
    mime_format = "jpeg" if mime_type == "jpg" else mime_type

    # PILImage to bytes
    img_bytes = BytesIO()
    img.save(img_bytes, format=mime_format)  # adjust this to the desired format
    img_bytes.seek(0)

    return send_file(img_bytes, mimetype=f'image/{mime_type}')  # adjust the mimetype accordingly

    # return send_from_directory(directory=upload_folder, path=filename)


@app.route('/downloadUrl', methods=['POST'])
def download_url():
    url = request.form['url']  # assuming filename is sent in the POST request body
    # response = requests.get(url, proxies={
    #     "http": "http://127.0.0.1:7890",
    #     "https": "http://127.0.0.1:7890"
    # })
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))

    # PILImage to bytes
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')  # adjust this to the desired format
    img_bytes.seek(0)

    return send_file(img_bytes, mimetype="image/jpeg")  # adjust the mimetype accordingly


def check_if_URL_valid(url):
    parsed_url = urlparse(url)

    return parsed_url.scheme and parsed_url.netloc


class InferParam(BaseModel):
    movie_id : str


@app.route('/infer', methods=['POST'])
@siwa.doc(form=InferParam,
          tags="/",
          summary="Given an image url or obs file path and a question, infer the answer.",
          )
def infer(form: InferParam):
    """
    This API endpoint takes an image and a question as input, and returns the answer to the question based on the image.
    """
    # Save the image file
    print("I'm in inference function.")
    print("Form: {}".format(form))
    movie_id = form.movie_id
    
    print("Current movie id: {}".format(movie_id))

    answer = summy_service.get_movie_structure(movie_id)
    print('Output: {}'.format(answer))
    return {'answer': answer}


if __name__ == '__main__':
    app.after_request(add_cors_headers)
    app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'png', 'jpeg', 'txt'}
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit file size to 16MB
    app.run(host='0.0.0.0', port=8010, debug=False)

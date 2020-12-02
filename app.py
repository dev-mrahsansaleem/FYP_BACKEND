import os
from os import mkdir
from os.path import isdir
from flask import Flask, flash, request, redirect, url_for
from flask_cors.decorator import cross_origin
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_cors import CORS


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# libs for image processing
# import numpy.core.multiarray
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from cv2 import *
import io
from base64 import b64encode
from json import dumps
from PIL import Image

# libs for image processing ^^^^^
app = Flask(__name__)
app.secret_key = "0122****"
CORS(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

UPLOAD_FOLDER = './Images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
# ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# print(cors.__str__())

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def get_response_image(image_path):
    with open(image_path, "rb") as img_file:
        encoded_Image = b64encode(img_file.read())

    # pil_img = Image.open(image_path, mode='r')
    # byte_arr = io.BytesIO()
    # pil_img.save(byte_arr, format='PNG')
    # encoded_Image = encodebytes(byte_arr.getvalue()).decode('base64')
    return encoded_Image.decode("utf-8")


def extraction(Brain_Image):
    Brain_Image = np.asarray(Brain_Image)
    # print(type(Brain_Image))
    gray = cv2.cvtColor(Brain_Image, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
    ret, markers = cv2.connectedComponents(thresh)
    marker_area = [
        np.sum(markers == m) for m in range(np.max(markers)) if m != 0
    ]
    largest_component = np.argmax(marker_area) + 1
    brain_mask = markers == largest_component
    brain_out = Brain_Image.copy()
    brain_out[brain_mask == False] = (0, 0, 0)
    return brain_out


def mainFun(inputImagePath):

    img_brain = cv2.imread(inputImagePath)
    height = 208
    width = 176
    dim = (width, height)
    # res_img = []
    res = cv2.resize(img_brain, dim, interpolation=cv2.INTER_LINEAR)
    # img = stringToImage(base64_URL)
    brain_extracted_img = extraction(res)
    # brain_extracted_base64_String = imageToString(brain_extracted_img)
    return brain_extracted_img


@app.route("/", methods=['GET', 'POST'])
def testFunction():
    return "Hello world"


@app.route("/api/uploadImage", methods=['GET', 'POST'])
@cross_origin()
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return {"status": "no file part added"}, 201
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return {"status": "no selected file"}, 201
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # filename = datetime.now().strftime("%Y_%m_%d_%H_%M_%S_")+filename

            if not isdir(app.config['UPLOAD_FOLDER']):
                mkdir(app.config['UPLOAD_FOLDER'])

            temp = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(temp)
            # print(temp)

            data = mainFun(temp)

            data = Image.fromarray(data)
            temp = os.path.join(app.config['UPLOAD_FOLDER'],
                                "extraction_" + filename)
            data.save(temp)
            encoded_extration_image = get_response_image(temp)
            # print(data)
            # ShowImage('Connected Components', data, 'rgb')

            return {
                "status": "success",
                "path": temp,
                "encoded_extration_image": encoded_extration_image
            }, 201
    else:
        return {"status": "request not found"}, 404


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=True)
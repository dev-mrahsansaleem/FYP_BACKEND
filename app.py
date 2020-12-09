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
    return encoded_Image.decode("utf-8")


def Resize(img):
    # image = np.asarray(img)
    resized_Img = cv2.resize(img, (208, 176), interpolation=cv2.INTER_LINEAR)
    return resized_Img


def Normalization(img):
    norm_img = np.zeros((800, 800))
    normalize_img = cv2.normalize(img, norm_img, 0, 255, cv2.NORM_MINMAX)
    return normalize_img


def extraction(Brain_Image):
    # final_image = plt.imshow(Brain_Image, cmap="gray")
    # final_image = plt.show()
    # print(type(Brain_Image))
    Brain_Image = np.asarray(Brain_Image)
    gray = cv2.cvtColor(Brain_Image, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
    ret, markers = cv2.connectedComponents(thresh)
    #Get the area taken by each component. Ignore label 0 since this is the background.
    marker_area = [
        np.sum(markers == m) for m in range(np.max(markers)) if m != 0
    ]
    #Get label of largest component by area
    largest_component = np.argmax(
        marker_area) + 1  #Add 1 since we dropped zero above
    #Get pixels which correspond to the brain
    brain_mask = markers == largest_component
    brain_out = Brain_Image.copy()
    #In a copy of the original image, clear those pixels that don't correspond to the brain
    brain_out[brain_mask == False] = (0, 0, 0)
    return brain_out


def Enhancement(en_img):
    #en_img=np.asarray(en_img)
    ret, enhancedImage = cv2.threshold(en_img, 130, 255, cv2.THRESH_TOZERO)
    return enhancedImage


def imageProcessing(inputImagePath, inputFileName):
    img_brain = cv2.imread(inputImagePath)
    Resized_image = Resize(img_brain)
    Normalized_image = Normalization(Resized_image)
    brain_extracted_img = extraction(Normalized_image)
    enhanced_brain_img = Enhancement(brain_extracted_img)

    # extrated saving and decodeing
    brain_extracted_img_File = Image.fromarray(brain_extracted_img)
    brain_extracted_img_Path = os.path.join(app.config['UPLOAD_FOLDER'],
                                            "extraction_" + inputFileName)
    brain_extracted_img_File.save(brain_extracted_img_Path)
    encoded_extration_image = get_response_image(brain_extracted_img_Path)

    # enhanced saving and decodeing
    enhanced_brain_img_File = Image.fromarray(enhanced_brain_img)
    brain_enhanced_img_Path = os.path.join(app.config['UPLOAD_FOLDER'],
                                           "enhanced_" + inputFileName)
    enhanced_brain_img_File.save(brain_enhanced_img_Path)
    encoded_enhanced_image = get_response_image(brain_enhanced_img_Path)

    return encoded_extration_image, encoded_enhanced_image


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

            inputImagePath = os.path.join(app.config['UPLOAD_FOLDER'],
                                          filename)
            file.save(inputImagePath)

            encoded_extration_image, encoded_enhanced_image = imageProcessing(
                inputImagePath, filename)

            return {
                "status": "success",
                "encoded_extration_image": encoded_extration_image,
                "encoded_enhanced_image": encoded_enhanced_image
            }, 201
    else:
        return {"status": "request not found"}, 404


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=True)
# import pandas as pd
# import matplotlib.pyplot as plt
# import io
# from json import dumps
from cv2 import *
import numpy as np
from base64 import b64encode
from os.path import isdir, join
from PIL import Image
from src import app


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
    brain_extracted_img_Path = join(app.config['UPLOAD_FOLDER'],
                                    "extraction_" + inputFileName)
    brain_extracted_img_File.save(brain_extracted_img_Path)
    encoded_extration_image = get_response_image(brain_extracted_img_Path)

    # enhanced saving and decodeing
    enhanced_brain_img_File = Image.fromarray(enhanced_brain_img)
    brain_enhanced_img_Path = join(app.config['UPLOAD_FOLDER'],
                                   "enhanced_" + inputFileName)
    enhanced_brain_img_File.save(brain_enhanced_img_Path)
    encoded_enhanced_image = get_response_image(brain_enhanced_img_Path)

    return encoded_extration_image, encoded_enhanced_image

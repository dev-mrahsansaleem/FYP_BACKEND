from src import app

import numpy as np
import cv2

from os.path import isdir, join

from PIL import Image


def Resize(img):
    # image = np.asarray(img)
    resized_Img = cv2.resize(img, (208, 176), interpolation=cv2.INTER_LINEAR)
    return resized_Img


def Normalization(img):
    norm_img = np.zeros((800, 800))
    normalize_img = cv2.normalize(img, norm_img, 0, 255, cv2.NORM_MINMAX)
    return normalize_img


def extraction(Brain_Image):
    Brain_Image = np.asarray(Brain_Image)
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


def imageProcessing(inputImagePath, inputFileName):
    img_brain = cv2.imread(inputImagePath)
    Resized_image = Resize(img_brain)
    Normalized_image = Normalization(Resized_image)
    brain_extracted_img = extraction(Normalized_image)
    enhanced_brain_img = Enhancement(brain_extracted_img)

    brain_extracted_img_File = Image.fromarray(brain_extracted_img)
    brain_extracted_img_Path = join(app.config['UPLOAD_FOLDER'],
                                    "extraction_" + inputFileName)
    brain_extracted_img_File.save(brain_extracted_img_Path)

    # enhanced saving and decodeing
    enhanced_brain_img_File = Image.fromarray(enhanced_brain_img)
    brain_enhanced_img_Path = join(app.config['UPLOAD_FOLDER'],
                                   "enhanced_" + inputFileName)
    enhanced_brain_img_File.save(brain_enhanced_img_Path)

    return brain_extracted_img_Path, brain_enhanced_img_Path


def Enhancement(en_img):
    ret, enhancedImage = cv2.threshold(en_img, 130, 255, cv2.THRESH_TOZERO)
    return enhancedImage

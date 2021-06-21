import shutil
import nibabel
import imageio

from src import app
from src.config.config import Images, db, images_schema
from src.helper.functions import token_required, allowed_file, storeImageInDp, get_response_image
from src.helper.machineLearningFunctions import imageProcessing

from math import floor
from flask.helpers import flash
from flask_cors.decorator import cross_origin
from flask import request, jsonify
from werkzeug.utils import secure_filename
from os import mkdir
from os.path import isdir, join, exists

# image routes


@cross_origin()
@app.route("/api/sendImage", methods=['POST'])
@token_required
def sendImage(current_user):
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Attach a file')
            return jsonify({"status": "no file part added"}), 404

        file = request.files['file']
        if file.filename == '':
            flash('Selected a file')
            return jsonify({"status": "image not attached to file"}), 404
        exten, isAllow = allowed_file(file.filename)
        if not isAllow:
            print(exten)
            return jsonify({"status": "invalid file type" + exten}), 404

        if not isdir(app.config['UPLOAD_FOLDER']):
            mkdir(app.config['UPLOAD_FOLDER'])

        if not isdir(app.config['UPLOAD_FOLDER'] + "/NII_FILES"):
            mkdir(app.config['UPLOAD_FOLDER'] + "/NII_FILES")

        if not isdir(app.config['UPLOAD_FOLDER'] + "/InputImage"):
            mkdir(app.config['UPLOAD_FOLDER'] + "/InputImage")

        if exten == 'nii':
            filename = secure_filename(file.filename)
            niifilePath = join(app.config['UPLOAD_FOLDER'] + "/NII_FILES",
                               filename)
            file.save(niifilePath)
            image_array = nibabel.load(niifilePath).get_data()
            total_volumes = image_array.shape[3]
            total_slices = image_array.shape[2]
            current_slice = floor(total_slices / 2)
            current_volume = floor(total_volumes / 2)
            data = image_array[:, :, current_slice, current_volume]

            filename = filename[:-4] + "_t" + "{:0>3}".format(
                str(current_volume + 1)) + "_z" + "{:0>3}".format(
                    str(current_slice + 1)) + ".png"
            if not exists(filename):
                imageio.imwrite(filename, data)
                print('Saved.')
            inputImagePath = join(app.config['UPLOAD_FOLDER'] + "/InputImage",
                                  filename)
            print('Moving files...')
            src = filename
            shutil.move(src, inputImagePath)
            print('Moved.')
            # TODO: convert file in png ans assign it's path to inputImagePath
        else:
            filename = secure_filename(file.filename)
            inputImagePath = join(app.config['UPLOAD_FOLDER'] + "/InputImage",
                                  filename)
            file.save(inputImagePath)

        brain_extracted_img_Path, brain_enhanced_img_Path = imageProcessing(
            inputImagePath, filename)

        inputImageId = storeImageInDp(inputImagePath, filename, None,
                                      current_user['public_id'])

        storeImageInDp(brain_extracted_img_Path, "extracted_" + filename,
                       inputImageId, current_user['public_id'])

        storeImageInDp(brain_enhanced_img_Path, "enhanced_" + filename,
                       inputImageId, current_user['public_id'])

        return jsonify({
            "status":
            "success " + str(inputImageId),
            "inputImagePath":
            get_response_image(inputImagePath),
            "encoded_extration_image":
            get_response_image(brain_extracted_img_Path),
            "encoded_enhanced_image":
            get_response_image(brain_enhanced_img_Path)
        }), 201


@cross_origin()
@app.route("/api/history", methods=['GET'])
@token_required
def getHistory(current_user):
    if request.method == "GET":
        queryResult = db.session.query(Images).filter(
            Images.createdby == current_user["public_id"])
        data = images_schema.dump(queryResult)

        for d in data:
            d["image"] = get_response_image(d["image"])

        return jsonify({
            "status": "OK",
            "data": data,
            "currentUser": current_user
        })

from src import app
from src.config.config import Images, db, images_schema

from flask.helpers import flash
from flask_cors.decorator import cross_origin
from flask import request, jsonify
from src.helper.functions import token_required, allowed_file, storeImageInDp, get_response_image
from src.helper.machineLearningFunctions import imageProcessing
from werkzeug.utils import secure_filename
from os import mkdir
from os.path import isdir, join


# image routes
@app.route("/api/sendImage", methods=['POST'])
@cross_origin()
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

        if not allowed_file(file.filename):
            return jsonify({"status": "invalid file type"}), 404

        filename = secure_filename(file.filename)
        if not isdir(app.config['UPLOAD_FOLDER']):
            mkdir(app.config['UPLOAD_FOLDER'])

        inputImagePath = join(app.config['UPLOAD_FOLDER'], filename)
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


@app.route("/api/history", methods=['GET'])
@cross_origin()
@token_required
def getHistory(current_user):
    if request.method == "GET":
        queryResult = db.session.query(Images).filter(
            Images.createdBy == current_user["public_id"])
        data = images_schema.dump(queryResult)

        for d in data:
            d["image"] = get_response_image(d["image"])

        return jsonify({
            "status": "OK",
            "data": data,
            "currentUser": current_user
        })

import shutil
import nibabel
import imageio
from tensorflow.keras.models import load_model
# from tf.keras.models import load_model
from keras.preprocessing.image import img_to_array, load_img

from src import app
from src.config.config import Images, db, images_schema
from src.helper.functions import allowed_image, token_required, allowed_file, storeImageInDp, get_response_image
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


@cross_origin()
@app.route("/api/model/vgg16", methods=['POST'])
@token_required
def vgg16(current_user):
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Attach a file')
            return jsonify({"status": "no file part added"}), 404

        file = request.files['file']
        if file.filename == '':
            flash('Selected a file')
            return jsonify({"status": "image not attached to file"}), 404

        exten, isAllow = allowed_image(file.filename)
        if not isAllow:
            print(exten)
            return jsonify({"status": "invalid file type" + exten}), 404

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

        if not isdir(app.config['MODEL_FOLDER']):
            return jsonify({"status": "model not found "}), 404

        model = load_model("./model/VGG16")
        print(model.summary())
        # model = load_model("\model\VGG16")
        img = load_img(brain_enhanced_img_Path)
        test_img = img_to_array(img)
        print("======Before============>>>", test_img.shape)
        test_img = test_img.reshape((1, ) + test_img.shape)
        print("=======after============>>>", test_img.shape)
        prediction = model.predict(test_img)  # error here
        print(prediction)
        return jsonify({"status": "OK", "prediction": prediction})


@cross_origin()
@app.route("/api/model/vgg19", methods=['POST'])
@token_required
def vgg19(current_user):
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Attach a file')
            return jsonify({"status": "no file part added"}), 404

        file = request.files['file']
        if file.filename == '':
            flash('Selected a file')
            return jsonify({"status": "image not attached to file"}), 404

        exten, isAllow = allowed_image(file.filename)
        if not isAllow:
            print(exten)
            return jsonify({"status": "invalid file type" + exten}), 404

        filename = secure_filename(file.filename)
        inputImagePath = join(app.config['UPLOAD_FOLDER'] + "/InputImage",
                              filename)
        file.save(inputImagePath)

        if isdir(app.config['MODEL_FOLDER']):

            model = load_model("./model/VGG19")
            print(model.summary())
            # model = load_model("\model\VGG16\VGG16_model")
            # img = load_img(inputImagePath)
            # test_img = img_to_array(img)
            # test_img = test_img.reshape((1, ) + test_img.shape)
            # prediction = model.predict(test_img)
            # print(prediction)
            return jsonify({"status": "OK", "prediction": prediction})
        else:
            return jsonify({"status": "model not found "}), 404


@cross_origin()
@app.route("/api/model/alexnet", methods=['POST'])
@token_required
def alexnet(current_user):
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Attach a file')
            return jsonify({"status": "no file part added"}), 404

        file = request.files['file']
        if file.filename == '':
            flash('Selected a file')
            return jsonify({"status": "image not attached to file"}), 404

        exten, isAllow = allowed_image(file.filename)
        if not isAllow:
            print(exten)
            return jsonify({"status": "invalid file type" + exten}), 404

        filename = secure_filename(file.filename)
        inputImagePath = join(app.config['UPLOAD_FOLDER'] + "/InputImage",
                              filename)
        file.save(inputImagePath)

        if isdir(app.config['MODEL_FOLDER']):

            model = load_model("./model/VGG16")
            print(model.summary())
            # model = load_model("\model\VGG16\VGG16_model")
            # img = load_img(inputImagePath)
            # test_img = img_to_array(img)
            # test_img = test_img.reshape((1, ) + test_img.shape)
            # prediction = model.predict(test_img)
            # print(prediction)
            return jsonify({"status": "OK", "prediction": prediction})
        else:
            return jsonify({"status": "model not found "}), 404


@cross_origin()
@app.route("/api/model/resnet", methods=['POST'])
@token_required
def resnet(current_user):
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Attach a file')
            return jsonify({"status": "no file part added"}), 404

        file = request.files['file']
        if file.filename == '':
            flash('Selected a file')
            return jsonify({"status": "image not attached to file"}), 404

        exten, isAllow = allowed_image(file.filename)
        if not isAllow:
            print(exten)
            return jsonify({"status": "invalid file type" + exten}), 404

        filename = secure_filename(file.filename)
        inputImagePath = join(app.config['UPLOAD_FOLDER'] + "/InputImage",
                              filename)
        file.save(inputImagePath)

        if isdir(app.config['MODEL_FOLDER']):

            model = load_model("./model/resnet")
            print(model.summary())
            model = load_model("\model\VGG16\VGG16_model")
            img = load_img(inputImagePath)
            test_img = img_to_array(img)
            test_img = test_img.reshape((1, ) + test_img.shape)
            prediction = model.predict(test_img)
            # print(prediction)
            return jsonify({"status": "OK", "prediction": prediction})
        else:
            return jsonify({"status": "model not found "}), 404
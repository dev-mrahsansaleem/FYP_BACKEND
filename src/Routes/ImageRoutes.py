from os import mkdir
from os.path import isdir, join
from flask import flash, request
from flask_cors.decorator import cross_origin
from werkzeug.utils import secure_filename
# from datetime import datetime
from base64 import b64encode
from src import app
import src.ML_Code.imageProcessing as IP

UPLOAD_FOLDER = './Images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def testFunction():
    return "Hello world..."


@app.route("/api/uploadImage", methods=['POST'])
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

            inputImagePath = join(app.config['UPLOAD_FOLDER'], filename)
            file.save(inputImagePath)

            encoded_extration_image, encoded_enhanced_image = IP.imageProcessing(
                inputImagePath, filename)

            return {
                "status": "success",
                "encoded_extration_image": encoded_extration_image,
                "encoded_enhanced_image": encoded_enhanced_image
            }, 201
    else:
        return {"status": "invalid request method"}, 404
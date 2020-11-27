import os
from os import mkdir
from os.path import isdir
from flask import Flask, flash, request, redirect, url_for
from flask_cors.decorator import cross_origin
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = "0122****"
CORS(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

UPLOAD_FOLDER = './Images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
# ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# print(cors.__str__())

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            return {"status": "success"}, 201
    else:
        return "invalid"


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=True)
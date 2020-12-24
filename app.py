from os import mkdir
from flask.helpers import flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors.decorator import cross_origin
from flask import Flask, request, jsonify, render_template
from datetime import datetime, timedelta
from os.path import isdir, join
from functools import wraps
from flask_cors import CORS
import uuid
import jwt
import numpy as np
from PIL import Image
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from base64 import b64encode
import cv2
from werkzeug.utils import secure_filename

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
UPLOAD_FOLDER = './images'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'iAmSecretkey'

currentENV = "pro"

if currentENV == "pro":
    app.config[
        'SQLALCHEMY_DATABASE_URI'] = 'postgres://dyoujoahgzwngd:0e8d96e971c5ed4b7b6c5a8852e0b18165ec4aa6c91b561390bcd08f8a992634@ec2-52-203-182-92.compute-1.amazonaws.com:5432/dgkc0vbh46sc8'
    print("production env")
else:
    app.host = "127.0.0.1"
    app.port = 5000
    app.debug = True
    app.use_reloader = True
    app.config[
        'SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost/FYP_TEMP_DB'
    print("devlopment env")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "0122****"
CORS(app)

# models

db = SQLAlchemy(app)
ma = Marshmallow(app)


class Users(db.Model):
    __tablename__ = 'tblUsers'
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(200), unique=True)
    username = db.Column(db.String(200), unique=True)
    password = db.Column(db.String(200))

    def __init__(self, public_id, username, password):
        self.public_id = public_id
        self.username = username
        self.password = password


class Images(db.Model):
    __tablename__ = "tblImages"
    id = db.Column(db.Integer, primary_key=True)
    imageName = db.Column(db.String(200))
    image = db.Column(db.Text())
    parentOf = db.Column(db.Integer)
    createdBy = db.Column(db.String(200))

    # -1 mean input image otherwise id of input image will be assign

    def __init__(self, imageName, image, parentOf, createdBy):
        self.imageName = imageName
        self.image = image
        self.parentOf = parentOf
        self.createdBy = createdBy


# Schemas


class UserSchema(ma.Schema):
    class Meta:
        fields = ('public_id', 'username', 'password')


user_schema = UserSchema()
users_schema = UserSchema(many=True)


class ImageSchema(ma.Schema):
    class Meta:
        fields = ('imageName', 'image', 'parentOf', 'createdBy')


image_schema = ImageSchema()
images_schema = ImageSchema(many=True)

# custom functions


def get_response_image(image_path):
    with open(image_path, "rb") as img_file:
        encoded_Image = b64encode(img_file.read())
    return encoded_Image.decode("utf-8")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def storeImageInDp(imagePath, imageName, parentOF, user_publicID):
    image = Images(imageName=imageName,
                   image=imagePath,
                   parentOf=parentOF,
                   createdBy=user_publicID)
    db.session.add(image)
    db.session.commit()
    db.session.flush()
    insertedId = image.id

    return insertedId

    # SQLCommand = " INSERT INTO FYP_TEMP_DB.dbo.tblImages (imageName,imagePath,parentImage,createdBy,createdAt) OUTPUT INSERTED.id VALUES (?,?,?,?,?)"
    # Values = [
    #     str(imageName),
    #     str(imagePath), parentOF,
    #     str(user_publicID),
    #     datetime.utcnow()
    # ]
    # print(Values)
    # cursor.execute(SQLCommand, Values)
    # imageId = cursor.fetchone()[0]
    # conn.commit()
    return -1


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
            # print("token in token_req" + token)
        if not token:
            return jsonify({"status": "no token found"}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            public_id = data['public_id']
            current_user = users_schema.dump(
                db.session.query(Users).filter(
                    Users.public_id == public_id))[0]
            # SQLCommand = f"SELECT * FROM tblUsers WHERE publicID = \'{public_id}\'"
            # SQLCommand = f"SELECT * FROM tblUsers WHERE username = \'{auth.username}\' AND  userpass = \'{auth.password}\'"
            # cursor.execute(SQLCommand)
            # current_user = "cursor.fetchone()"
        except:
            return jsonify({"status": "invalid token"}), 401

        return f(current_user, *args, **kwargs)

    return decorated


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


@app.route('/')
@cross_origin()
def webPage():
    return "working"


# user routes


@app.route('/api/register', methods=['POST'])
@cross_origin()
def register():
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'status': ' Body not found'}), 200
        publicID = str(uuid.uuid4())
        username = data['username']
        hashed_Pass = generate_password_hash(data['password'], method='sha256')

        if db.session.query(Users).filter(
                Users.username == username).count() != 0:
            return jsonify({'status': username + ' already exist'}), 200

        userData = Users(publicID, username, hashed_Pass)
        db.session.add(userData)
        db.session.commit()
        # data = user_schema.dump(userData) #this can b pass to jsonify
        return jsonify({'status': 'ok', "public_id": publicID}), 201
    else:
        return jsonify({'status': 'request type not found'}), 405


@app.route('/api/login', methods=['POST'])
@cross_origin()
def login():
    if request.method == 'POST':
        auth = request.authorization
        print(auth)
        if not auth or not auth.username or not auth.password:
            return jsonify({"status": "auth no found"}), 200

        if db.session.query(Users).filter(
                Users.username == auth.username).count() == 0:
            return jsonify({"status": "User not found"}), 200
        else:
            data = users_schema.dump(
                db.session.query(Users).filter(
                    Users.username == auth.username))

            username = data[0]['username']
            password = data[0]['password']
            publicID = data[0]['public_id']

            # return jsonify(data)

            if check_password_hash(password, auth.password):
                token = jwt.encode(
                    {
                        'public_id': publicID,
                        'exp': datetime.utcnow() + timedelta(minutes=30)
                    }, app.config['SECRET_KEY'])

                return jsonify({'token': token.decode('utf-8')}), 201
            return jsonify({"status": "Invalid Password"}), 404
    else:
        return jsonify({'status': 'request type not found'}), 405


# user routes
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


if __name__ == "__main__":
    app.run()

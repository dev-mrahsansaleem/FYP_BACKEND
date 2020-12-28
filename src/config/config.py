import sqlalchemy
from src import app

from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

UPLOAD_FOLDER = './images'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'iAmSecretkey'

currentENV = "pro"

if currentENV == "pro":
    app.config[
        'SQLALCHEMY_DATABASE_URI'] = 'postgres://dyoujoahgzwngd:0e8d96e971c5ed4b7b6c5a8852e0b18165ec4aa6c91b561390bcd08f8a992634@ec2-52-203-182-92.compute-1.amazonaws.com:5432/dgkc0vbh46sc8'
    print("production env")
else:
    # app.host = ["127.0.0.100"]
    # app.port = 6000
    app.debug = True
    app.config[
        'SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost/FYP_TEMP_DB'
    print("devlopment env")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "0122****"

db = SQLAlchemy(app)
ma = Marshmallow(app)

# models


class Users(db.Model):
    __tablename__ = 'tblUsers'
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(200), unique=True)
    username = db.Column(db.String(200), unique=True)
    password = db.Column(db.String(200))
    createdOn = db.Column(db.String(200))

    def __init__(self, public_id, username, password):
        self.public_id = public_id
        self.username = username
        self.password = password

    def __init__(self, public_id, username, password, createdOn):
        self.public_id = public_id
        self.username = username
        self.password = password
        self.createdOn = createdOn


class UserSchema(ma.Schema):
    class Meta:
        fields = ('public_id', 'username', 'password', 'createdOn')


user_schema = UserSchema()
users_schema = UserSchema(many=True)

# Image model


class Images(db.Model):
    __tablename__ = "tblImages"
    id = db.Column(db.Integer, primary_key=True)
    imageName = db.Column(db.String(200))
    image = db.Column(db.Text())
    parentOf = db.Column(db.Integer)
    createdBy = db.Column(db.String(200))
    createdOn = db.Column(db.String(200))

    # -1 mean input image otherwise id of input image will be assign

    def __init__(self, imageName, image, parentOf, createdBy):
        self.imageName = imageName
        self.image = image
        self.parentOf = parentOf
        self.createdBy = createdBy

    def __init__(self, imageName, image, parentOf, createdBy, createdOn):
        self.imageName = imageName
        self.image = image
        self.parentOf = parentOf
        self.createdBy = createdBy
        self.createdOn = createdOn


# Schemas


class ImageSchema(ma.Schema):
    class Meta:
        fields = ('imageName', 'image', 'parentOf', 'createdBy', 'createdOn')


image_schema = ImageSchema()
images_schema = ImageSchema(many=True)

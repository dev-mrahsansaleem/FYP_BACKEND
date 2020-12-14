from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

UPLOAD_FOLDER = './Images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'iAmSecret'

app.secret_key = "0122****"
CORS(app)

from src.Routes import ImageRoutes
from src.Routes import UserRoutes

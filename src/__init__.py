from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

app.secret_key = "0122****"
CORS(app)

from src.Routes import ImageRoutes
from flask import Flask

app = Flask(__name__)

# config
from src.config import config

# routes
from src.routes import rootRoute
from src.routes import userRoutes
from src.routes import imageRoutes
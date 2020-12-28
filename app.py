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
import cv2
from werkzeug.utils import secure_filename

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

CORS(app)

# models

# custom functions

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
# return -1

# user routes

if __name__ == "__main__":
    app.run()

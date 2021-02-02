from base64 import b64encode
from datetime import datetime
from src.config.config import Users, Images, db, users_schema
from flask import request, jsonify
from functools import wraps
from src import app
import jwt

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def get_response_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            encoded_Image = b64encode(img_file.read())
        return encoded_Image.decode("utf-8")
    except:
        return "notFound"
        pass


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def storeImageInDp(imagePath, imageName, parentOF, user_publicID):
    image = Images(imageName=imageName,
                   image=imagePath,
                   parentOf=parentOF,
                   createdBy=user_publicID,
                   createdOn=str(datetime.utcnow()))
    db.session.add(image)
    db.session.commit()
    db.session.flush()
    insertedId = image.id

    return insertedId


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
            data = jwt.decode(token,
                              app.config['SECRET_KEY'],
                              algorithms=["HS256"])
            public_id = data['public_id']
            current_user = users_schema.dump(
                db.session.query(Users).filter(
                    Users.public_id == public_id))[0]
        except:
            return jsonify({"status": "invalid token"}), 401

        return f(current_user, *args, **kwargs)

    return decorated

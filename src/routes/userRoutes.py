from src import app
from src.config.config import db, Users, users_schema

from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors.decorator import cross_origin
from flask import request, jsonify
from datetime import datetime, timedelta
import uuid
import jwt

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

        userData = Users(publicID, username, hashed_Pass,
                         str(datetime.utcnow()))
        # print(userData.createdOn)
        db.session.add(userData)
        db.session.commit()
        # data = user_schema.dump(userData) #this can b pass to jsonify
        return jsonify({
            'status': 'ok',
            "public_id": publicID,
        }), 201
    else:
        return jsonify({'status': 'request type not found'}), 405


@app.route('/api/login', methods=['POST'])
@cross_origin()
def login():
    if request.method == 'POST':
        auth = request.authorization
        # print(auth)
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
                        'exp': datetime.utcnow() + timedelta(hours=30)
                    },
                    app.config['SECRET_KEY'],
                    algorithm="HS256")

                return jsonify({
                    'token': token,
                    "data": data,
                    "username": username
                }), 201
            return jsonify({"status": "Invalid Password"}), 404
    else:
        return jsonify({'status': 'request type not found'}), 405

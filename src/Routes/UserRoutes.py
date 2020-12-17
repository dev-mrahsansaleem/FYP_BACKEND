from datetime import datetime, timedelta
from flask import request, jsonify
from flask.helpers import make_response
from flask_cors.decorator import cross_origin
from werkzeug.security import generate_password_hash, check_password_hash
from src import app
from src.config.dbConfig import conn, cursor
from src.common.functions import token_required
import uuid
import jwt


@app.route('/api/user', methods=['GET'])
@token_required
def get_All_Users(current_user):
    SQLCommand = "SELECT * FROM tblUsers"

    cursor.execute(SQLCommand)
    output = []

    for row in cursor.fetchall():
        user = {}
        user['publicID'] = row.publicID
        user['username'] = row.username
        user['password'] = row.userpass
        output.append(user)
    conn.commit()

    if output.__len__() == 0:
        return jsonify({'status': 'There is no user'}), 404
    return jsonify({'users': output})


@app.route('/api/user/<public_id>', methods=['GET'])
@token_required
def get_single_User(public_id):
    SQLCommand = f"SELECT * FROM tblUsers WHERE publicID = \'{public_id}\'"

    cursor.execute(SQLCommand)
    row = cursor.fetchone()

    if not row:
        return jsonify({'status': 'User not found check public id'}), 404

    user = {}
    user['publicID'] = row.publicID
    user['username'] = row.username
    user['password'] = row.userpass
    return jsonify({'user': user})


@app.route('/api/user/<public_id>', methods=['DELETE'])
def delete_user(public_id):

    SQLCommand = f"SELECT * FROM tblUsers WHERE publicID = \'{public_id}\'"

    cursor.execute(SQLCommand)
    row = cursor.fetchone()

    if not row:
        return jsonify({'status': 'User not found check public id'}), 404

    SQLCommand = f"DELETE FROM tblUsers WHERE publicID = \'{public_id}\'"

    cursor.execute(SQLCommand)
    conn.commit()
    return jsonify({'status': 'User deleted successfull'})


@app.route('/api/register', methods=['POST'])
@cross_origin()
def register():
    data = request.get_json()
    publicID = str(uuid.uuid4())
    username = data['username']
    hashed_Pass = generate_password_hash(data['password'], method='sha256')

    # print(publicID + " " + str(publicID.__len__()))
    # print(username + " " + str(username.__len__()))
    # print(hashed_Pass + " " + str(hashed_Pass.__len__()))
    try:
        SQLCommand = " INSERT INTO FYP_TEMP_DB.dbo.tblUsers (publicID,username,userpass) VALUES (?,?,?)"
        Values = [
            publicID,
            username,
            hashed_Pass,
        ]

        cursor.execute(SQLCommand, Values)
        conn.commit()
    except:
        return jsonify({'status': username + ' already exist'}), 200

    return jsonify({'status': username + ' created', 'public': publicID}), 201


@app.route('/api/login')
@cross_origin()
def login():
    auth = request.authorization
    # print(auth)
    if not auth or not auth.username or not auth.password:
        return jsonify({"status": "auth no correct"})

    SQLCommand = f"SELECT * FROM tblUsers WHERE username = \'{auth.username}\'"
    # SQLCommand = f"SELECT * FROM tblUsers WHERE username = \'{auth.username}\' AND  userpass = \'{auth.password}\'"

    cursor.execute(SQLCommand)
    user = cursor.fetchone()

    if not user:
        return jsonify({"status": "User not found"})

    if check_password_hash(user.userpass, auth.password):
        token = jwt.encode(
            {
                'public_id': user.publicID,
                'exp': datetime.utcnow() + timedelta(minutes=30)
            }, app.config['SECRET_KEY'])

        return jsonify({'token': token.decode('UTF-8')}), 201
    return jsonify({"status": "Invalid Password"})

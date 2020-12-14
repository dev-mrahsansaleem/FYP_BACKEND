from functools import wraps
from flask import request
from flask.json import jsonify
from src.config.dbConfig import cursor
from src import app

import jwt


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({"status": "no token found"}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            public_id = data['public_id']
            SQLCommand = f"SELECT * FROM tblUsers WHERE publicID = \'{public_id}\'"
            # SQLCommand = f"SELECT * FROM tblUsers WHERE username = \'{auth.username}\' AND  userpass = \'{auth.password}\'"
            cursor.execute(SQLCommand)
            current_user = cursor.fetchone()
        except:
            return jsonify({"status": "invalid token"}), 401

        return f(current_user, *args, **kwargs)

    return decorated
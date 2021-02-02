from src import app
from src.helper.functions import token_required

from flask_cors.decorator import cross_origin
from flask import jsonify


@app.route('/')
@cross_origin()
def webPage():
    return "working"


@app.route('/api/testTokken')
@cross_origin()
@token_required
def testTokken(current_user):
    return jsonify({"status": "tokken is valid"})

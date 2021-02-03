from src import app
from src.helper.functions import token_required

from flask_cors.decorator import cross_origin
from flask import request, jsonify


@app.route('/')
@cross_origin()
def webPage():
    return "working"

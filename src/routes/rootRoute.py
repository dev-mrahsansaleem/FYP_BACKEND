from src import app

from flask_cors.decorator import cross_origin


@app.route('/')
@cross_origin()
def webPage():
    return "working"

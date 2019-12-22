from . import api_blueprint as api
from flask import jsonify

@api.route('/')
def index():
    return jsonify({'message': 'hello, world'})
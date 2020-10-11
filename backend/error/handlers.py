from backend.api import api
from backend.error.errors import APIError
from flask import jsonify


@api.errorhandler(APIError)
def handler(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

from flask import Blueprint
from helpers import issue_token, token_required

routes_api = Blueprint('api', __name__)

prefix = "/api"

@routes_api.after_request
def set_default_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Accept"] = "application/json"
    response.headers["Content-Type"] = "application/json"
    return response

@routes_api.route(prefix + '/login', methods=["POST"])
def login():
    user_id = 1

    token = issue_token(user_id, seconds=6000)

    return {"data": token}

@routes_api.route(prefix + '/generate_url', methods=["POST"])
@token_required
def generate_url():
    return "success"

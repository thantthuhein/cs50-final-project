from flask import Blueprint, request, jsonify, session
from db import db
from sqlalchemy import select
from models import User, ShortUrl
from werkzeug.security import check_password_hash
from helpers import issue_token, token_required, invalidate_token, generate_short_url, validate_url, get_user_from_token

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
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username:
        return jsonify({"data": {"message": "Username is required"}}), 422

    elif not password:
        return jsonify({"data": {"message": "Password is required"}}), 422

    result = db.session.execute(
        select(User).where(User.username == username)
    )

    user = result.scalars().first()

    if user is None or not check_password_hash(user.password, password):
        return jsonify({"data": {"message": "Invalid Credentials"}}), 422

    token = issue_token(user.id, seconds=864000)

    return jsonify({"data": {
        "access_token": token,
        "message": "Success"
    }}), 200

@routes_api.route(prefix + '/logout', methods=["POST"])
def logout():
    headers = request.headers
    bearer = headers.get('Authorization')
    token = bearer.split()[1]

    invalidate_token(token)

    return {"data": {"message": "Success"}}

@routes_api.route(prefix + '/generate_url', methods=["POST"])
@token_required
def generate_url():
    data = request.get_json()
    long_url = data.get("long_url", "")

    if not long_url:
        return jsonify({"data": {"message": "URL is required"}}), 422

    if not validate_url(long_url):
        return jsonify({"data": {"message": "URL is invalid"}}), 422

    short_url = generate_short_url()

    headers = request.headers
    bearer = headers.get('Authorization')
    token = bearer.split()[1]

    user = get_user_from_token(token)

    if not user:
        return jsonify({"data": {"message": "Something went wrong"}}), 400

    shortUrl = ShortUrl.create(
        user_id=user.id,
        short_url=short_url,
        long_url=long_url
    )

    return jsonify({"data": {
        "message": "Success",
        "short_url": shortUrl.short_url
    }}), 200

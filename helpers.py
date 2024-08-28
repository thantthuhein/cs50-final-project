from flask import redirect, session, request
from datetime import datetime, timezone, timedelta
from functools import wraps
from models import Token, User, ShortUrl
from sqlalchemy import select
from db import db
import dotenv
import jwt
import os
import random
import string
import validators
import requests

dotenv.load_dotenv()

secret = os.getenv('JWT_SECRET')
algorithm = os.getenv('JWT_ALGORITHM') or "HS256"

def login_required(f):
    """
    Decorate routes to require web login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def token_required(f):
    """
    Decorate routes to require jwt token.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None

        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]

        if not token:
            return {
                "message": "Authentication Token is missing!",
                "error": "Unauthorized"
            }, 401
        try:
            data=jwt.decode(token, secret, algorithms=[algorithm])

            validation = validate_token(data)

            if not validation == None:
                return validation

            return f(*args, **kwargs)
        except Exception as e:
            return {
                "message": "Something went wrong",
                "error": str(e)
            }, 500

    return decorated_function

def issue_token(user_id, seconds = 900):
    if not secret:
        raise Exception("Secret Key not found.")

    token = Token.create(user_id)

    payload = {
        'id': token.uuid,
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(seconds=seconds),
    }

    return jwt.encode(payload, secret, algorithm)

def validate_token(data):
    if not "user_id" in data:
        return {
            "message": "Token is invalid!",
            "error": "Unauthorized"
        }, 401

    if not "id" in data:
        return {
            "message": "Token is invalid!",
            "error": "Unauthorized"
        }, 401

    if not "exp" in data:
        return {
            "message": "Token is invalid!",
            "error": "Unauthorized"
        }, 401

    user_id = data["user_id"]
    result = db.session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalars().first()

    if user is None:
        return {
            "message": "Invalid User!",
            "error": "Unauthorized"
        }, 401

    token_id = data["id"]

    result = db.session.execute(
        select(Token).where(Token.uuid == token_id)
    )
    token = result.scalars().first()

    if token is None:
        return {
            "message": "Expired Token!!!",
            "error": "Unauthorized"
        }, 401

    if token.revoked is True:
        return {
            "message": "Expired Token!",
            "error": "Unauthorized"
        }, 401

    return None

def invalidate_token(token):
    if not token:
        return False

    decodedToken = decode_jwt_token(token)

    if decodedToken is None:
        return False

    if not decodedToken["id"]:
        return False

    try:
        result = db.session.execute(
            select(Token).where(Token.uuid == decodedToken['id'])
        )
        token = result.scalars().first()

        if token:
            token.revoked = True
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise
    finally:
        db.session.close()

    return True

def decode_jwt_token(token):
    try:
        return jwt.decode(token, secret, algorithm)
    except:
        return None

def generate_short_url():
    """Generate a random string of 6 characters."""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=8))

def validate_url(url):
    if is_valid_url(url):
        if is_url_reachable(url):
            return True
        else:
            return False
    else:
        return False

def is_valid_url(url):
    return validators.url(url)

def is_url_reachable(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)

        return response.status_code < 400
    except requests.RequestException:
        return False

def get_user_from_token(token):
    if not token:
        return False

    decodedToken = jwt.decode(token, secret, algorithm)

    if not decodedToken["id"]:
        return False

    userQuery = db.session.execute(
        select(User).where(User.id == decodedToken['user_id'])
    )
    user = userQuery.scalars().first()

    if user is None:
        return False

    return user

def add_visits(short_url):
    try:
        query = db.session.execute(
            select(ShortUrl).where(ShortUrl.short_url == short_url)
        )
        url_map = query.scalars().first()

        if url_map:
            current_visits = url_map.visits
            url_map.visits = current_visits + 1
            db.session.commit()
            return True

        return False
    except Exception as e:
        db.session.rollback()
        raise
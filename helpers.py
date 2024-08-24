from flask import redirect, session, request
from datetime import datetime, timezone, timedelta
from functools import wraps
from models import Token, User
from sqlalchemy import select
from db import db
import dotenv
import jwt
import os

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
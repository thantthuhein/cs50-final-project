from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
from db import db
from sqlalchemy import select
import uuid

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def create(username, password):
        created_at = datetime.now(timezone.utc)

        user = User(
            username=username,
            password=password,
            created_at=created_at,
        )

        db.session.add(user)
        db.session.commit()

        return user

    def __repr__(self):
        return self

class Token(db.Model):
    __tablename__ = "access_tokens"

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(200), nullable=False, unique=True)
    user_id = db.Column(db.Integer, nullable=False)
    revoked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def create(user_id):
        created_at = datetime.now(timezone.utc)
        token_id = uuid.uuid4()

        token = Token(
            uuid=str(token_id),
            user_id=user_id,
            revoked=False,
            created_at=created_at,
        )

        db.session.add(token)
        db.session.commit()

        return token

    def __repr__(self):
        return self

class ShortUrl(db.Model):
    __tablename__ = "short_urls"

    id = db.Column(db.Integer, primary_key=True)
    short_url = db.Column(db.String(10), nullable=False, unique=True)
    long_url = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    visits = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    def create(user_id, short_url, long_url):
        created_at = datetime.now(timezone.utc)

        shortenUrl = ShortUrl(
            short_url=short_url,
            long_url=long_url,
            user_id=user_id,
            visits=0,
            created_at=created_at,
        )

        db.session.add(shortenUrl)
        db.session.commit()

        return shortenUrl

    def __repr__(self):
        return self

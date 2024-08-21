from datetime import datetime, timezone
from db import db

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
            created_at=created_at
        )

        db.session.add(user)
        db.session.commit()

        return user

    def __repr__(self):
        return self
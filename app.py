import os
from flask import Flask
from db import db
from routes import routes
from routes_api import routes_api
from flask_session import Session

app = Flask(__name__)

app.config["APP_KEY"] = os.getenv("APP_KEY")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shorturl.db'
db.init_app(app)

with app.app_context():
    db.create_all()

app.register_blueprint(routes)
app.register_blueprint(routes_api)

if __name__ == "__main__":
    app.run(debug=True)
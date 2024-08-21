from flask import Flask
from db import db
from routes import routes
from flask_session import Session

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shorturl.db'
db.init_app(app)

def initialize_db():
    with app.app_context():
        db.create_all()

initialize_db()

app.register_blueprint(routes)

if __name__ == "__main__":
    app.run(debug=True)
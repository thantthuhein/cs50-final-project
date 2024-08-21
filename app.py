from flask import Flask
from db import db
from routes import routes

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shorturl.db'
db.init_app(app)

def initialize_db():
    with app.app_context():
        db.create_all()

initialize_db()

app.register_blueprint(routes)

if __name__ == "__main__":
    app.run(debug=True)
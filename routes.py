from flask import Blueprint

# Create a Blueprint for your routes
routes = Blueprint('main', __name__)

@routes.route('/')
def main():
    return "URL Shortener"

@routes.route('/index')
def index():
    return "index"
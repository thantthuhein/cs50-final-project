from flask import Blueprint, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import login_required, add_visits
from sqlalchemy import select
from models import User, ShortUrl
from db import db

routes = Blueprint('web', __name__)

@routes.route('/')
def main():
    return redirect("login")

@routes.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if session.get('user_id'):
        return redirect("dashboard")

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        validation_errors = validateRegister(request.form)

        if validation_errors is not None:
            return validation_errors

        try:
            password_hash = generate_password_hash(password)

            user = User.create(username, password_hash)

            session["user_id"] = user.id

            return redirect("dashboard")
        except:
            session["status"] = "Username already exists!"
            return render_template("register.html")

    if session.get("status"):
        session.pop('status')
    return render_template("register.html")

@routes.route("/login", methods=["GET", "POST"])
def login():
    if session.get('user_id'):
        return redirect("dashboard")

    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            session["status"] = "Must provide username!"
            return render_template("login.html")

        elif not request.form.get("password"):
            session["status"] = "Must provide password!"
            return render_template("login.html")

        username = request.form.get("username")
        requestPassword = request.form.get("password")

        result = db.session.execute(
            select(User).where(User.username == username)
        )

        user = result.scalars().first()

        if user is None or not check_password_hash(user.password, requestPassword):
            session["status"] = "Invalid username or password!"
            return render_template("login.html")

        session["user_id"] = user.id

        return redirect("dashboard")

    else:
        return render_template("login.html")

@routes.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    user_id = session.get("user_id")

    query = db.session.execute(
        select(ShortUrl).where(ShortUrl.user_id == user_id)
    )
    url_maps = query.scalars().all()

    return render_template("dashboard.html", url_maps=url_maps)

@routes.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    return redirect("login")

def validateRegister(form):
    username = form.get("username")
    password = form.get("password")
    confirm_password = form.get("confirmation")

    if not username:
        session["status"] = "Username must be filled!"
        return render_template("register.html")

    if not password:
        session["status"] = "Password must be filled!"
        return render_template("register.html")

    if not confirm_password:
        session["status"] = "Confirm Password must be filled!"
        return render_template("register.html")

    if not password == confirm_password:
        session["status"] = "Two passwords must be the same!"
        return render_template("register.html")

    return None

@routes.route("/<short_url>", methods=["GET"])
def redirect_to_url(short_url):
    result = db.session.execute(
        select(ShortUrl).where(ShortUrl.short_url == short_url)
    )
    url_map = result.scalars().first()

    if not url_map:
        return "<H1>404</H1>", 404

    add_visits(short_url)

    return redirect(url_map.long_url)
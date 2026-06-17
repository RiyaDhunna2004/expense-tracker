from flask import Blueprint, render_template, request, redirect, session
from database.mongo import users_collection
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # First check email exists
        existing_user = users_collection.find_one({
            "email": email
        })

        if existing_user:
            return render_template(
                "signup.html",
                error="Email already used!"
            )

        # Then check password match
        if password != confirm_password:
            return render_template(
                "signup.html",
                error="Passwords do not match!"
            )

        hashed_password = generate_password_hash(password)

        users_collection.insert_one({
            "name": name,
            "email": email,
            "password": hashed_password
        })

        return redirect("/login")

    return render_template("signup.html")

# Login
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = users_collection.find_one({"email": email})

        if user and check_password_hash(user["password"], password):
            session["user_id"] = str(user["_id"])
            session["name"] = user["name"]
            if "remember_me" in request.form:
                session.permanent = True
            else:
                session.permanent = False
            return redirect("/dashboard")

        return render_template("login.html", error="Invalid username or password!")
    return render_template("login.html")


# Logout
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
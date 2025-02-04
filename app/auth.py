from flask import Blueprint, request, jsonify, g
from werkzeug.security import check_password_hash, generate_password_hash
from .models import User
from .extensions import db
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    unset_jwt_cookies,
    set_access_cookies,
    set_refresh_cookies,
    get_jwt,
    verify_jwt_in_request,
)
from .tools import response_template
from sqlalchemy.exc import IntegrityError
from datetime import timedelta, datetime, timezone

auth = Blueprint("auth", __name__, url_prefix="/")

PROTECTED_ENDPOINTS = {"/create"}


@auth.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if not username:
            error = "Enter your username"
        elif not email:
            error = "Enter your email"
        elif not password:
            error = "Enter your password"
        else:
            try:
                password_hash = generate_password_hash(password)
                new_user = User(
                    Username=username, Email=email, Password_hashed=password_hash
                )
                db.session.add(new_user)
                db.session.commit()
            except IntegrityError:
                error = f"User {username} is already registered."
            else:
                return response_template(
                    True, "Create account successfully!", status_code=201
                )
    return response_template(False, error, status_code=400)


@auth.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not username:
            error = "Enter your username"
        elif not password:
            error = "Enter your password"
        else:
            user = User.query.filter_by(Username=username).one()
            if not user or not check_password_hash(user.Password_hashed, password):
                error = "Invalid username or password"
        if error == None:
            access_token = create_access_token(
                identity=user.Username, expires_delta=timedelta(hours=12)
            )
            refresh_token = create_refresh_token(
                identity=user.Username, expires_delta=timedelta(days=20)
            )
            response = response_template(
                True,
                "Login successful",
            )
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            return response
    return response_template(False, error, status_code=401)


@auth.route("/logout", methods=["GET", "POST"])
def logout():
    if request.method == "POST":
        response = jsonify({"msg": "Logged out"})
        unset_jwt_cookies(response)
    return response


@auth.route("/refresh", methods=["GET", "POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    new_access_token = create_access_token(identity=identity)
    refresh_token_exp = get_jwt()["exp"]  # 获取 refresh_token 过期时间（时间戳）
    now = datetime.now(timezone.utc).timestamp()
    remaining_time = refresh_token_exp - now  # 剩余时间（秒）
    response = response_template(
        True,
        "Refresh successful",
    )
    set_access_cookies(response, new_access_token)
    if remaining_time < 86400:
        new_refresh_token = create_refresh_token(identity=identity)
        set_refresh_cookies(response, new_refresh_token)

    return response


@auth.before_app_request
def auto_login():
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        if identity:
            g.user = User.query.get(identity)
        else:
            g.user = None
    except Exception as e:
        g.user = None
    if not g.user and request.path in PROTECTED_ENDPOINTS:
        return response_template(
            False,
            "Authentication required",
            {
                "login_url": "/login",
            },
            status_code=401,
        )

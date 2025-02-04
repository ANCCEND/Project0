import os
from flask import Flask
from .models import User,Post
from config import Config 


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(Config)

    from .extensions import db, migrate, jwt

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from .auth import auth
    from .blog import blog

    app.register_blueprint(auth)
    app.register_blueprint(blog)

    return app



import pymysql
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from app.extensions import db


# 数据库模型
class User(db.Model):
    id = db.Column( db.Integer, primary_key=True)
    Username = db.Column(db.String(50), unique=True, nullable=False)
    Email = db.Column(db.String(120), unique=True, nullable=False)
    Password_hashed = db.Column(db.String(300), nullable=False)

    def __repr__(self):
        return f"<User {self.Username}>"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(120), nullable=False)
    Content = db.Column(db.Text, nullable=False)
    Category = db.Column(db.String(40), nullable=False)
    Date = db.Column(db.DateTime)
    User_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    author = db.relationship("User", backref=db.backref("posts", lazy=True))

    def __repr__(self):
        return f"<Post {self.Title}>"

from database import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    # id (int), username (string), password (string), role (string)
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # Default role is 'user'
from flask_bcrypt import Bcrypt
from sqlalchemy.orm import relationship, backref
from datetime import timedelta
from flask_jwt_extended import create_access_token
from ..models import db
from app.models.root_model import RootModel


class User(RootModel):
    """ user table definition """

    _tablename_ = "users"

    # fields of the user table
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), unique=True)
    username = db.Column(db.String(256), nullable=False, default="")
    password = db.Column(db.String(256), nullable=False, default="")
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __init__(self, username, email, password):
        """ initialize with email, username and password """
        self.email = email
        self.username = username
        self.password = Bcrypt().generate_password_hash(password).decode()

    # to be used on login
    def password_is_valid(self, password):
        """ checks the password against it's hash to validate the user's password """
        return Bcrypt().check_password_hash(self.password, password)

    # to be used to generate user token
    def generate_token(self, user):
        """ generates the access token """
        # set token expiry period
        expiry = timedelta(days=10)

        return create_access_token(user, expires_delta=expiry)

    def __repr__(self):
        return "<User: {}>".format(self.email)

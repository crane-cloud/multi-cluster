
from ..models import db
from app.models.root_model import RootModel


class Product(RootModel):
    """ product table definition """

    _tablename_ = "products"

    # fields of the product table
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False, unique=True)
    size = db.Column(db.Integer)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    price = db.Column(db.Integer, nullable=False, default=0)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())

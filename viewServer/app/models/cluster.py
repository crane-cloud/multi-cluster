
from ..models import db
from app.models.root_model import RootModel


class Cluster(RootModel):
    """ cluster table definition """

    _tablename_ = "clusters"

    # fields of the product table
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False, unique=True)
    cluster_id = db.Column(db.String(256), nullable=False, unique=True)
    ip_address = db.Column(db.String(256), nullable=False, unique=True)
    port = db.Column(db.Integer, nullable=False, default=0)
    chosen_cluster = db.Column(db.String(256), nullable=True, default=None)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())

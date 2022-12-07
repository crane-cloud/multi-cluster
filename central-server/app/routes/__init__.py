from flask_restful import Api
from app.controllers import (
    IndexView, ClusterView, ClusterDetailView)


api = Api()

# Index route
api.add_resource(IndexView, '/')

# Cluster routes
api.add_resource(ClusterView, '/clusters', endpoint='clusters')
api.add_resource(ClusterDetailView, '/clusters/<string:cluster_id>',
                 endpoint='cluster')

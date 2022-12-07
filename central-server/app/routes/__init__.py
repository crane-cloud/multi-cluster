from flask_restful import Api
from app.controllers import (
    IndexView, UserView, UserDetailView, UserLoginView, ResetPassword,
    ClusterView, ClusterDetailView)


api = Api()

# Index route
api.add_resource(IndexView, '/')

# User routes
api.add_resource(UserView, '/users', endpoint='users')
api.add_resource(UserDetailView, '/users/<string:user_id>',
                 endpoint='user')
api.add_resource(UserLoginView, '/users/login', endpoint='user_login')
api.add_resource(ResetPassword, '/users/reset_password',
                 endpoint='reset_password')

# Cluster routes
api.add_resource(ClusterView, '/clusters', endpoint='clusters')
api.add_resource(ClusterDetailView, '/clusters/<string:cluster_id>',
                 endpoint='cluster')

from flask_restful import Api
from app.controllers import (
    IndexView, UserView, UserDetailView, UserLoginView, ResetPassword,
    ProductView, ProductDetailView)


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

# Product routes
api.add_resource(ProductView, '/products', endpoint='products')
api.add_resource(ProductDetailView, '/products/<string:product_id>',
                 endpoint='product')

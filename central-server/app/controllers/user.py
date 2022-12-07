import json
from flask_restful import Resource, request

from app.schemas import UserSchema, UserLoginSchema
from app.models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt


class UserView(Resource):

    def post(self):
        """
        Creating a User Account
        """
        user_schema = UserSchema()

        user_data = request.get_json()

        validated_user_data, errors = user_schema.load(user_data)

        if errors:
            return dict(status='fail', message=errors), 400

        existing_user = User.find_first(email=validated_user_data["email"])

        if existing_user:
            return dict(status='fail',
                        message=f'User email {validated_user_data["email"]} already exists'), 409

        user = User(**validated_user_data)

        saved_user = user.save()

        if not saved_user:
            return dict(status='fail', message='Internal Server Error'), 500

        new_user_data, errors = user_schema.dumps(user)

        return dict(status='success', data=dict(user=json.loads(new_user_data))), 201

    @jwt_required
    def get(self):
        """
        Getting All users
        """
        user_schema = UserSchema(many=True)

        users = User.find_all()

        users_data, errors = user_schema.dumps(users)

        if errors:
            return dict(status="fail", message="Internal Server Error"), 500

        return dict(status="success", data=dict(users=json.loads(users_data))), 200


class UserDetailView(Resource):

    def get(self, user_id):
        """
        Getting individual user
        """
        schema = UserSchema()

        user = User.get_by_id(user_id)

        if not user:
            return dict(status="fail", message=f"User with id {user_id} not found"), 404

        user_data, errors = schema.dumps(user)

        if errors:
            return dict(status="fail", message=errors), 500

        return dict(status='success', data=dict(user=json.loads(user_data))), 200

    @jwt_required
    def patch(self, user_id):
        """
        Update a single user
        """

        # To do check if user is admin
        schema = UserSchema(partial=True)

        update_data = request.get_json()

        validated_update_data, errors = schema.load(update_data)

        if errors:
            return dict(status="fail", message=errors), 400

        user = User.get_by_id(user_id)

        if not user:
            return dict(status="fail", message=f"User with id {user_id} not found"), 404

        updated_user = User.update(user, **validated_update_data)

        if not updated_user:
            return dict(status='fail', message='Internal Server Error'), 500

        return dict(status="success", message="User updated successfully"), 200

    def delete(self, user_id):
        """
        Delete a single user
        """

        user = User.get_by_id(user_id)

        if not user:
            return dict(status="fail", message=f"User with id {user_id} not found"), 404

        deleted_user = user.delete()

        if not deleted_user:
            return dict(status='fail', message='Internal Server Error'), 500

        return dict(status='success', message="Successfully deleted"), 200


class UserLoginView(Resource):

    def post(self):
        """
        """
        user_schema = UserLoginSchema()
        token_schema = UserSchema()

        login_data = request.get_json()

        validated_user_data, errors = user_schema.load(login_data)

        if errors:
            return dict(status='fail', message=errors), 400

        email = validated_user_data.get('email', None)
        password = validated_user_data.get('password', None)

        user = User.find_first(email=email)

        if not user:
            return dict(status='fail', message="login failed"), 401

        user_dict, errors = token_schema.dump(user)

        if user and user.password_is_valid(password):

            access_token = user.generate_token(user_dict)

            if not access_token:
                return dict(
                    status="fail",
                    message="Internal Server Error"
                ), 500

            return dict(
                status='success',
                data=dict(
                    access_token=access_token,
                    email=user.email,
                    username=user.username,
                    id=str(user.id),
                )), 200

        return dict(status='fail', message="login failed"), 401


class ResetPassword(Resource):
    def post(self):
        """
        Update a single user
        """

        # To do check if user is admin
        schema = UserLoginSchema()

        update_data = request.get_json()

        validated_update_data, errors = schema.load(update_data)

        if errors:
            return dict(status="fail", message=errors), 400

        user = User.find_first(email=validated_update_data["email"])

        if not user:
            return dict(status="fail", message=f"User with email {validated_update_data['email']} not found"), 404

        password_hash = Bcrypt().generate_password_hash(
            validated_update_data["password"]).decode()

        updated_user = User.update(
            user, password=password_hash)

        if not updated_user:
            return dict(status='fail', message='Internal Server Error'), 500

        return dict(status="success", message="User password reset successfully"), 200

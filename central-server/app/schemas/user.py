from marshmallow import Schema, fields


class UserSchema(Schema):

    id = fields.Integer(dump_only=True)
    email = fields.Email()
    username = fields.String()
    password = fields.String(load_only=True)


class UserLoginSchema(Schema):

    id = fields.Integer(dump_only=True)
    email = fields.Email(required=True)
    username = fields.String()
    password = fields.String(load_only=True, required=True)

from marshmallow import Schema, fields


class ProductSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    size = fields.Integer()
    quantity = fields.Integer(required=True)
    price = fields.Integer(required=True)

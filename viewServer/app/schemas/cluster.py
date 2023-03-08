from marshmallow import Schema, fields


class ClusterSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    cluster_id = fields.String(required=True)
    ip_address = fields.String(required=True)
    port = fields.Integer(required=True)
    chosen_cluster = fields.String()
    date_created = fields.DateTime(dump_only=True)

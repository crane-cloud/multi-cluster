import json
from flask_restful import Resource, request
from app.schemas import ClusterSchema
from app.models.cluster import Cluster


class ClusterView(Resource):

    def post(self):
        """
        Adding a Cluster
        """
        cluster_schema = ClusterSchema()

        cluster_data = request.get_json()

        validated_cluster_data, errors = cluster_schema.load(cluster_data)

        if errors:
            return dict(status='fail', message=errors), 400

        existing_cluster = Cluster.find_first(
            name=validated_cluster_data["name"])

        if existing_cluster:
            return dict(status='fail',
                        message=f'Cluster with name {validated_cluster_data["name"]} already exists'), 409

        cluster = Cluster(**validated_cluster_data)

        saved_cluster = cluster.save()

        if not saved_cluster:
            return dict(status='fail', message='Internal Server Error'), 500

        new_cluster_data, errors = cluster_schema.dumps(cluster)

        return dict(status='success', data=dict(cluster=json.loads(new_cluster_data))), 201

    def get(self):
        """
        Getting All clusters
        """
        cluster_schema = ClusterSchema(many=True)

        clusters = Cluster.find_all()

        clusters_data, errors = cluster_schema.dumps(clusters)

        if errors:
            return dict(status="fail", message="Internal Server Error"), 500

        return dict(status="success", data=dict(clusters=json.loads(clusters_data))), 200


class ClusterDetailView(Resource):

    def get(self, cluster_id):
        """
        Getting an individual cluster
        """
        schema = ClusterSchema()

        cluster = Cluster.get_by_id(cluster_id)

        if not cluster:
            return dict(status="fail", message=f"Cluster with id {cluster_id} not found"), 404

        cluster_data, errors = schema.dumps(cluster)

        if errors:
            return dict(status="fail", message=errors), 500

        return dict(status='success', data=dict(cluster=json.loads(cluster_data))), 200


    def patch(self, cluster_id):
        """
        Update a single cluster
        """
        # To do check if cluster is admin
        schema = ClusterSchema(partial=True)

        update_data = request.get_json()

        validated_update_data, errors = schema.load(update_data)

        if errors:
            return dict(status="fail", message=errors), 400

        cluster = Cluster.get_by_id(cluster_id)

        if not cluster:
            return dict(status="fail", message=f"Cluster with id {cluster_id} not found"), 404

        updated_cluster = Cluster.update(cluster, **validated_update_data)

        if not updated_cluster:
            return dict(status='fail', message='Internal Server Error'), 500

        return dict(status="success", message="Cluster updated successfully"), 200

    def delete(self, cluster_id):
        """
        Delete a single cluster
        """
        cluster = Cluster.get_by_id(cluster_id)

        if not cluster:
            return dict(status="fail", message=f"Cluster with id {cluster_id} not found"), 404

        deleted_cluster = cluster.delete()

        if not deleted_cluster:
            return dict(status='fail', message='Internal Server Error'), 500

        return dict(status='success', message="Successfully deleted"), 200

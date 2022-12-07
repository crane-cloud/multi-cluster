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
        # Check for duplication
        existing_cluster = Cluster.find_first(
            name=validated_cluster_data["name"])

        if existing_cluster:
            return dict(status='fail',
                        message=f'Cluster with name {validated_cluster_data["name"]} already exists'), 409

        existing_cluster = Cluster.find_first(
            cluster_id=validated_cluster_data["cluster_id"])

        if existing_cluster:
            return dict(status='fail',
                        message=f'Cluster with id {validated_cluster_data["cluster_id"]} already exists'), 409

        existing_cluster = Cluster.find_first(
            ip_address=validated_cluster_data["ip_address"])

        if existing_cluster:
            return dict(status='fail',
                        message=f'Cluster with ip address {validated_cluster_data["ip_address"]} already exists'), 409

        cluster = Cluster(**validated_cluster_data)

        saved_cluster = cluster.save()

        if not saved_cluster:
            return dict(status='fail', message='Internal Server Error'), 500

        # get all clusters
        clusters = Cluster.find_all()
        clusters_schema = ClusterSchema(many=True)
        clusters_data, errors = clusters_schema.dumps(clusters)

        if errors:
            return dict(status='fail', message='Internal Server Error'), 500

        return dict(status='success', clusters=json.loads(clusters_data)), 201

    def get(self):
        """
        Getting All clusters
        """
        cluster_schema = ClusterSchema(many=True)

        clusters = Cluster.find_all()

        clusters_data, errors = cluster_schema.dumps(clusters)

        if errors:
            return dict(status="fail", message="Internal Server Error"), 500

        return dict(status="success", clusters=json.loads(clusters_data)), 200


class ClusterDetailView(Resource):

    def get(self, cluster_id):
        """
        Getting an individual cluster
        """
        schema = ClusterSchema()

        cluster = Cluster.find_first(cluster_id=cluster_id)

        if not cluster:
            return dict(status="fail", message=f"Cluster with id {cluster_id} not found"), 404

        cluster_data, errors = schema.dumps(cluster)

        if errors:
            return dict(status="fail", message=errors), 500

        return dict(status='success', cluster=json.loads(cluster_data)), 200

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

        cluster = Cluster.find_first(cluster_id=cluster_id)

        if not cluster:
            return dict(status="fail", message=f"Cluster with id {cluster_id} not found"), 404

        #check for duplication
        if "name" in validated_update_data:
            existing_cluster = Cluster.find_first(
                name=validated_update_data["name"])
        
            if existing_cluster and existing_cluster.id != cluster.id:
                return dict(status='fail',
                            message=f'Cluster with name {validated_update_data["name"]} already exists'), 409
        if "cluster_id" in validated_update_data:
            existing_cluster = Cluster.find_first(
                cluster_id=validated_update_data["cluster_id"])

            if existing_cluster and existing_cluster.id != cluster.id:
                return dict(status='fail',
                            message=f'Cluster with id {validated_update_data["cluster_id"]} already exists'), 409
        if "ip_address" in validated_update_data:
            existing_cluster = Cluster.find_first(
                ip_address=validated_update_data["ip_address"])

            if existing_cluster and existing_cluster.id != cluster.id:
                return dict(status='fail',
                            message=f'Cluster with ip address {validated_update_data["ip_address"]} already exists'), 409


        updated_cluster = Cluster.update(cluster, **validated_update_data)

        if not updated_cluster:
            return dict(status='fail', message='Internal Server Error'), 500

        return dict(status="success", message="Cluster updated successfully"), 200

    def delete(self, cluster_id):
        """
        Delete a single cluster
        """
        cluster = Cluster.find_first(cluster_id=cluster_id)

        if not cluster:
            return dict(status="fail", message=f"Cluster with id {cluster_id} not found"), 404

        deleted_cluster = cluster.delete()

        if not deleted_cluster:
            return dict(status='fail', message='Internal Server Error'), 500

        return dict(status='success', message="Successfully deleted"), 200

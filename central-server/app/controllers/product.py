import json
from flask_restful import Resource, request
from app.schemas import ProductSchema
from app.models.product import Product


class ProductView(Resource):

    def post(self):
        """
        Adding a Product
        """
        product_schema = ProductSchema()

        product_data = request.get_json()

        validated_product_data, errors = product_schema.load(product_data)

        if errors:
            return dict(status='fail', message=errors), 400

        existing_product = Product.find_first(
            name=validated_product_data["name"])

        if existing_product:
            return dict(status='fail',
                        message=f'Product with name {validated_product_data["name"]} already exists'), 409

        product = Product(**validated_product_data)

        saved_product = product.save()

        if not saved_product:
            return dict(status='fail', message='Internal Server Error'), 500

        new_product_data, errors = product_schema.dumps(product)

        return dict(status='success', data=dict(product=json.loads(new_product_data))), 201

    def get(self):
        """
        Getting All products
        """
        product_schema = ProductSchema(many=True)

        products = Product.find_all()

        products_data, errors = product_schema.dumps(products)

        if errors:
            return dict(status="fail", message="Internal Server Error"), 500

        return dict(status="success", data=dict(products=json.loads(products_data))), 200


class ProductDetailView(Resource):

    def get(self, product_id):
        """
        Getting an individual product
        """
        schema = ProductSchema()

        product = Product.get_by_id(product_id)

        if not product:
            return dict(status="fail", message=f"Product with id {product_id} not found"), 404

        product_data, errors = schema.dumps(product)

        if errors:
            return dict(status="fail", message=errors), 500

        return dict(status='success', data=dict(product=json.loads(product_data))), 200


    def patch(self, product_id):
        """
        Update a single product
        """
        # To do check if product is admin
        schema = ProductSchema(partial=True)

        update_data = request.get_json()

        validated_update_data, errors = schema.load(update_data)

        if errors:
            return dict(status="fail", message=errors), 400

        product = Product.get_by_id(product_id)

        if not product:
            return dict(status="fail", message=f"Product with id {product_id} not found"), 404

        updated_product = Product.update(product, **validated_update_data)

        if not updated_product:
            return dict(status='fail', message='Internal Server Error'), 500

        return dict(status="success", message="Product updated successfully"), 200

    def delete(self, product_id):
        """
        Delete a single product
        """
        product = Product.get_by_id(product_id)

        if not product:
            return dict(status="fail", message=f"Product with id {product_id} not found"), 404

        deleted_product = product.delete()

        if not deleted_product:
            return dict(status='fail', message='Internal Server Error'), 500

        return dict(status='success', message="Successfully deleted"), 200

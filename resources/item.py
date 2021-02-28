from typing import Text
from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from models.item import ItemModel
import requests


    
class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name',
                        type=Text,
                        required=True,
                        help="This field cannot be left blank!"
                        )
    
    @jwt_required()
    def get(self):
        data = Item.parser.parse_args()
        item = ItemModel.find_by_name(data['name'])
        if item:
            return item.json()
        return {'message': 'Item not found'}, 404
    
    @jwt_required()
    def post(self):
        data = Item.parser.parse_args()
        if ItemModel.find_by_name(data['name']):
            return {'message': "An item with name '{}' already exists.".format(data['name'])}, 400

        url = f"http://api.ipstack.com/{data['name']}?access_key=75c5dc00c321ae103780a846fe59e797&format=1"
        response = requests.get(url)
        response_data = response.json()

        if response_data['longitude'] == None:
            return {'message': 'IP or Website address not found, please write a correct data of ip or website address'}, 400


        api_data = {"longitude": response_data['longitude'], "latitude": response_data['latitude']}

        item = ItemModel(data['name'], **api_data)

        try:
            item.save_to_db()
        except:
            return {"message": "An error occurred inserting the item."}, 500

        return item.json(), 201

    @jwt_required()
    def delete(self):
        data = Item.parser.parse_args()
        item = ItemModel.find_by_name(data['name'])
        if item:
            item.delete_from_db()
            return {'message': 'Item deleted.'}
        return {'message': 'Item not found.'}, 404
    
    @jwt_required()
    def put(self, name):
        data = Item.parser.parse_args()
        item = ItemModel.find_by_name(data['name'])

        if item:
            item.longitude = data['longitude']
            item.latitude = data['latitude']
        else:
            item = ItemModel(**data)

        item.save_to_db()

        return item.json()


class ItemList(Resource):
    @jwt_required()
    def get(self):
        return {'items': list(map(lambda x: x.json(), ItemModel.query.all()))}

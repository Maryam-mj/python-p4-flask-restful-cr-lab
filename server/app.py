#!/usr/bin/env python3

from flask import Flask, request
from flask_migrate import Migrate
from flask_restful import Api, Resource
from sqlalchemy.exc import IntegrityError

from models import db, Plant

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = True

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

class Plants(Resource):
    def get(self):
        plants = Plant.query.all()
        return [p.to_dict() for p in plants], 200

    def post(self):
        data = request.get_json()
        if not data:
            return {"error": "JSON body required"}, 400

        name = data.get("name")
        image = data.get("image")
        price = data.get("price")

        if not name or not image or price is None:
            return {"error": "name, image, and price are required"}, 400

        try:
            new_plant = Plant(name=name, image=image, price=price)
            db.session.add(new_plant)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"error": "Database error"}, 500

        return new_plant.to_dict(), 201

class PlantByID(Resource):
    def get(self, id):
        plant = Plant.query.get(id)
        if not plant:
            return {"error": "Plant not found"}, 404
        return plant.to_dict(), 200

api.add_resource(Plants, "/plants")
api.add_resource(PlantByID, "/plants/<int:id>")

if __name__ == '__main__':
    app.run(port=5555, debug=True)

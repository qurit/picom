import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
dramatiq.set_broker(RabbitmqBroker(host="rabbitmq"))

from bson.json_util import dumps
from bson.objectid import ObjectId

from flask import Flask, request
from flask_restx import Resource, Api, fields
from flask_pymongo import PyMongo
from flask_cors import CORS

# import dicom.utils
# from dicom.echo import echo
from config import BaseConfig

config = BaseConfig()

app = Flask(__name__)
app.config.from_object(config)
app.url_map.strict_slashes = False
CORS(app, resources={r'/*': {'origins': '*'}})


mongo = PyMongo(app)
db = mongo.db

from api.encoders import jsonify
from api.routes.modalities import api as ns_api
api = Api(app)
api.add_namespace(ns_api)


@dramatiq.actor
def count_words(url):
    print(f"There are ${url}.")


@api.route('/hello')
class HelloWorld(Resource):

    def get(self):
        mongo.db.modalities.insert_one({'aet': 'MIT', 'port': 4000, 'address': 'localhost'})
        count_words.send('wtkns.dev')
        return {'hello': 'world'}



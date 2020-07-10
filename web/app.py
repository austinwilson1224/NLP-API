from flask import Flask,request,jsonify
from flask_restful import Api,Resource

from pymongo import MongoClient

# creating app and api
app = Flask(__name__)
api = Api(app)

# creating database instance
client = MongoClient("mongodb://db:27017")


@app.route('/')
def hello():
    return "hello world!"

if __name__ == "__main__":
    app.run('0.0.0.0')


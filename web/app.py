from flask import Flask,request,jsonify
from flask_restful import Api,Resource

from pymongo import MongoClient

import bcrypt
import spacy

# creating app and api
app = Flask(__name__)
api = Api(app)

# creating database instance
client = MongoClient("mongodb://db:27017")
db = client.SimilarityDB
users = db["Users"]


# check if the user is in the system
def userExist(username):
    if users.find({"username":username}).count() == 0:
        return False
    else:
        return True

# check if password is valid
def validPw(username,password):
    hashed_pw = users.find({
        "username":username
    })[0]["password"]
    
    
    if bcrypt.hashpw(password.encode('utf8'),hashed_pw) == hashed_pw:
        return True
    else:
        return False


def countTokens(username):
    return users.find({
        "username": username
    })[0]["tokens"]



class Register(Resource):
    def post(self):
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]

        # check to see if the user is already in the system
        if userExist(username):
            retJson = {
                "status": 301,
                "message": "username already in use"
            }
            return jsonify(retJson)

        # encrypt the password for security
        hashed_pw = bcrypt.hashpw(password.encode('utf8'),bcrypt.gensalt())

        # store the new user in the system
        users.insert({
            "username": username,
            "password": hashed_pw,
            "tokens": 6
        })
        retJson = {
            "status": 200,
            "message": "new user created"
        }
        return jsonify(retJson)
        
class Detect(Resource):
    def post(self):
        # store the different items 
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]
        text1 = postedData["text1"]
        text2 = postedData["text2"]

        # check if the user exists and send error if not 
        if not userExist(username):
            retJson = {
                "status": 301,
                "message":  "user not in the system"
            }
            return jsonify(retJson)
        
        # check if the password is valid ...
        if not validPw(username,password):
            retJson = {
                "status": 302,
                "message": "invalid password"
            }
            return jsonify(retJson)

        # verify number of tokens
        numTokens = countTokens(username)
        if numTokens <= 0:
            retJson = {
                "status": 303,
                "message": "you're out of tokens"
            }
            return jsonify(retJson)

        # calculate edit distance
        nlp = spacy.load('en_core_web_sm')
        text1 = nlp(text1)
        text2 = nlp(text2)
        ratio = text1.similarity(text2)

        # update the number of tokens
        current_tokens = countTokens(username)
        users.update({
            "username":username,
        },{
            "$set":{
                "tokens": current_tokens - 1
            }
        })
        return jsonify({
            "status": 200,
            "similarity": ratio,
            "message": "similarity score calculated successfully" 
        })

class Refill(Resource):
    def post(self):
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["admin_pw"]
        refill_amount = postedData["refill"] 
        # check user exists 
        if not userExist(username):
            retJson = {
                "status": 301,
                "message": "user DNE"
            }
            return jsonify(retJson)
        correctPass = "123"
        if not password == correctPass:
            retJson = {
                "status": 302,
                "message": "invalid password"
            }
            return jsonify(retJson)
        # refill the tokens
        currentTokens = countTokens(username)
        users.update({
            "username":username
        },{
            "$set":{
                "tokens":refill_amount + currentTokens
            }
        })
        return jsonify({
            "status": 200,
            "message": "refilled tokens"
        })
        

api.add_resource(Register,'/register')
api.add_resource(Detect,'/detect')
api.add_resource(Refill,'/refill')

@app.route('/')
def hello():
    return "hello world!"

if __name__ == "__main__":
    app.run('0.0.0.0')


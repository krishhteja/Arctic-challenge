from flask import Flask, render_template ,session, escape, request, Response
from flask import url_for, redirect, send_from_directory
from flask import send_file, make_response, abort
import uuid
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

from lora import DatabaseManager

app = Flask(__name__)
app.secret_key="arcticChallenge"

db = DatabaseManager()

#List of endpoints. What functions they would trigged on being called
@app.route('/')
def basic_pages(**kwargs):
    return make_response(open('index.html').read())

@app.route('/visual')
def visual():
    return make_response(open('visual.html').read())

@app.route('/getToken', methods=['POST'])
def getToken():
    return db.getToken(), 200, {'Content-Type': 'application/json'}

@app.route('/getData', methods=['POST'])
def getData():
    return db.getData(), 200, {'Content-Type': 'application/json'}

@app.route('/showData', methods=['POST'])
def showData():
    timeInfo = request.json['time']
    id = request.json['id']
    return db.showData(timeInfo, id), 200, {'Content-Type': 'application/json'}

@app.route('/getEntities', methods=['POST'])
def getEntities():
    return db.getEntities(), 200, {'Content-Type': 'application/json'}

app.run(host=os.getenv('IP', '0.0.0.0'),port=int(os.getenv('PORT', 5000)))

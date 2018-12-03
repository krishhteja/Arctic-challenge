import requests
import pymongo
from pymongo import MongoClient
from flask import Flask, jsonify, request
from datetime import datetime
from datetime import timedelta
import uuid, json
import dateutil.parser as parser
import hashlib

MONGO_HOST = "WRITE YOUR MONGO HOST."
MONGO_PORT = 23456 #INT VALUE ... PORT GOES HERE
MONGO_DB = "DATABASE NAME"
MONGO_USER = "USERNAME"
MONGO_PASS = "PASSWORD"
connection = MongoClient(MONGO_HOST, MONGO_PORT)
mongo = connection[MONGO_DB]
token = ''

class DatabaseManager:

    #Get token from SSiO server
    def getToken(self):
        url = "http://130.240.134.128:9000/oauth2/token"
        payload = "grant_type=password&username=user01ssr%40ssr.se&password=password&client_id=8f2e5c99050b48348a5badfe68b55a67&client_secret=48f18ebe9120476a8e852f157dcf9ff5"
        headers = {
            'Authorization': "Basic OGYyZTVjOTkwNTBiNDgzNDhhNWJhZGZlNjhiNTVhNjc6NDhmMThlYmU5MTIwNDc2YThlODUyZjE1N2RjZjlmZjU=",
            'Content-Type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache",
            'Postman-Token': "129ea1c9-ba6c-489f-b696-f5e3487d3b9e"
        }
        response = requests.request("POST", url, data=payload, headers=headers)
        data = response.json()
        global token
        token = data['access_token']
        print(token)
        return jsonify({"status":"success","token":data['access_token']})

    # Get data from SSiO server suing the token attained by getToken
    def getData(self):
        url = "https://130.240.134.128:3000/v1/queryContext"
        
        headers = {
            "Content-Type": "application/json",
            "X-Auth-Token": token
        }

        #Connect to mongodb on collection entities
        sensor = mongo.entities
        sensorArr = []
        for q in sensor.find({}):
            sensorInfo = {}
            sensorInfo['id'] = q['name']
            sensorInfo['type'] = 'LORA_Sensor'
            sensorInfo['isPattern'] = 'false'
            sensorArr.append(sensorInfo)
        mapData = {}
        #connect to the SSiO servers and get measurements with the list of sensor IDs
        mapData['entities'] = sensorArr
        data = json.dumps(mapData)
        currTime = datetime.today()
        try:
            response = requests.post(url,data=data, headers=headers, verify=False)
        except Exception as e:
            print(e)
            return e
        #Read the received measurements and save them to the mongo collection named "lora"
        responseData = response.json()
        connect = mongo.lora
        contextResp = (responseData['contextResponses'])
        mapForMongo = {}
        for element in contextResp:
            eachAttr = element['contextElement']
            idData = eachAttr['id']
            attr = eachAttr['attributes']
            localMap = {}
            for individualAttr in attr:
                name = individualAttr['name']
                value = individualAttr['value']
                localMap[name] = value
            localMap['recvTime'] = currTime
            localMap['sensorId'] = idData
            connect.insert(localMap)
        return jsonify({"status":"success"})

    #Get data from mongo to show on front-end ... Common for both visual.html and index.html
    def showData(self,time,sensor):
        connect = mongo.lora
        query = {}
        dateCheckEnd = parser.parse(time)
        dateCheckStart = dateCheckEnd - timedelta(hours=10)
        if sensor != "all":
            query['sensorId'] = sensor
        query['recvTime'] = {"$gte": dateCheckStart, "$lte":dateCheckEnd}
        respMap = {}
        print(query)
        for q in connect.find(query):
            mapToRespond = {}
            mapToRespond['nitro'] = q['NO2']
            mapToRespond['pm1'] = q['PM1']
            mapToRespond['pm10'] = q['PM10']
            mapToRespond['pm25'] = q['PM25']
            mapToRespond['lat'] = q['LAT']
            mapToRespond['time'] = q['Timestamp']
            mapToRespond['lon'] = q['LON']
            mapToRespond['dateTime'] = q['recvTime']
            ts = str(q['_id'])
            respMap[ts] = mapToRespond
        return jsonify({"status":"success","data":respMap})

    #Get all entities (sensor id's) from mongo to populate in visual.html
    def getEntities(self):
        connect = mongo.entities
        query = {}
        mapResp = []
        for q in connect.find(query):
            mapResp.append(q['name'])
        return jsonify({"status":"success",'data':mapResp})

    #This is NOT optimized code. Lot of code can be optimized
# -*- coding: utf-8 -*-

import config

from pymongo import MongoClient

try:
    client = MongoClient(config.MONGO_URI)
except:
    print("Failed to connect to server {}".format(config.MONGO_URI))

db = client.tbot

import json

def savedata(datahash, data):
    hashdoc = {'datahash': datahash}
    datadoc = {'data': data}

    lasthash = db.lasthash

    try:
        lastcode = [l for l in lasthash.find()][-1]['datahash']
    except:
        lastdata = db.lastdata
        lastdata.drop()
        lastdata.insert(datadoc)
        lasthash.drop()
        lasthash.insert(hashdoc)

        return

    if datahash != lastcode:
        lastdata = db.lastdata
        lastdata.drop()
        lastdata.insert(datadoc)
        lasthash.drop()
        lasthash.insert(hashdoc)

def getdata():
    col = db.lastdata

    doc = [d for d in col.find()][-1]

    data = json.loads(doc['data'])
    
    return data

from flask import request
from flask import jsonify
from models import AnalyticsModel
import os

AnalyticsModelTable = AnalyticsModel.Analytics(f"{os.getcwd()}/database/TrinHubDB.db")

def getAnalytics_processRequest():
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="GET":
        return jsonify(AnalyticsModelTable.get_events()["message"])
    elif request.method=="POST":
        return jsonify(AnalyticsModelTable.log_event(event_details=request.json)["message"])
    else:
        return {}
    

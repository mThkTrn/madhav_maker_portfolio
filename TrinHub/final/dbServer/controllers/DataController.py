from flask import request
from flask import jsonify
from models import CommunicationsModel
from models import ClubsModel
from models import UsersModel
from models import ClubMembershipsModel
from models import ClubMeetingsModel
from models import AnalyticsModel
import os

ClubsModelTable = ClubsModel.Club(f"{os.getcwd()}/database/TrinHubDB.db")
ClubMeetingsModelTable = ClubMeetingsModel.Meeting(f"{os.getcwd()}/database/TrinHubDB.db")
UsersModelTable = UsersModel.User(f"{os.getcwd()}/database/TrinHubDB.db")
ClubMembershipsModelTable = ClubMembershipsModel.ClubMemberships(f"{os.getcwd()}/database/TrinHubDB.db")
AnalyticsModelTable = AnalyticsModel.Analytics(f"{os.getcwd()}/database/TrinHubDB.db")
CommunicationsModelTable = CommunicationsModel.Communications(f"{os.getcwd()}/database/TrinHubDB.db")


def downloadDB():
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="GET":
        clubData = ClubsModelTable.getAllData()["message"]
        userData = UsersModelTable.getAllData()["message"]
        ClubMembershipsData = ClubMembershipsModelTable.getAllData()["message"]
        ClubMeetingData = ClubMeetingsModelTable.getAllData()["message"]
        ClubCommunicationData = CommunicationsModelTable.getAllData()["message"]
        AnalyticsData = AnalyticsModelTable.getAllData()["message"]

        allDBData = {"clubs":clubData, "users":userData, "clubMemberships":ClubMembershipsData, "meetings":ClubMeetingData, "communications":ClubCommunicationData, "analytics": AnalyticsData}
        return jsonify(allDBData)
    else:
        return {}

# CAN ADD CODE TO UPLOAD DB LATER
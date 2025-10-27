from flask import request
from flask import jsonify
from models import CommunicationsModel
from models import ClubsModel
from models import UsersModel
from models import ClubMembershipsModel
import os
from datetime import datetime, timedelta

CommunicationsModelTable = CommunicationsModel.Communications(f"{os.getcwd()}/database/TrinHubDB.db")
ClubsModelTable = ClubsModel.Club(f"{os.getcwd()}/database/TrinHubDB.db")
UsersModelTable = UsersModel.User(f"{os.getcwd()}/database/TrinHubDB.db")
ClubMembershipsTable = ClubMembershipsModel.ClubMemberships(f"{os.getcwd()}/database/TrinHubDB.db")

def getClubCommunications(clubName):
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="GET":
        clubId = ClubsModelTable.get_clubId_from_name(name=clubName)["message"]
        clubsCommunications = CommunicationsModelTable.get_clubs_communications(clubId=clubId)["message"]
        clubsCommunications = [communication for communication in clubsCommunications if communication["status"]==1]
        
        clubsCommunications = [communication for communication in clubsCommunications if datetime.now()-datetime.strptime(communication["date"], "%Y-%m-%d")<timedelta(days=7)]

        communications = []
        for i in range(len(clubsCommunications)):
            communication = clubsCommunications[i]
            communication["sender"] = UsersModelTable.get_officialName_from_userId(id=communication["senderId"])["message"]
            communication["club"] = ClubsModelTable.get_name_from_clubId(id=communication["clubId"])["message"]
            del communication["senderId"]
            del communication["clubId"]
            communications.append(clubsCommunications[-1])

        return jsonify(communications)
    else:
        return {}

def createClubCommunication_updateClubCommunication_deleteClubCommunication(clubName):
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="POST":
        data = request.json
        clubId = ClubsModelTable.get_clubId_from_name(name=clubName)["message"]
        
        data = request.json
        data["clubId"] = clubId
        data["senderId"] = UsersModelTable.get_userId_from_officialName(request.officialName)["message"]
        communication = CommunicationsModelTable.create_communication(communication_details=data)["message"]

        return jsonify(communication)
    elif request.method=="PUT":
        data = request.json

        return jsonify(CommunicationsModelTable.update_communication(id=data["id"], message=data["message"])["message"])
    elif request.method=="DELETE":
        return jsonify(CommunicationsModelTable.delete_communication(id=id)["message"])
    else:
        return {}

def updateCommunicationStatus(id):
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="PUT":
        data = request.json
        
        return jsonify(CommunicationsModelTable.update_communication_status(id=id, message=data["status"])["message"])
    else:
        return {}
    

def getLatestUsersCommunications():
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="GET":
        officialName = request.officialName
        userId = UsersModelTable.get_userId_from_officialName(officialName=officialName)["message"]
        usersClubs = ClubMembershipsTable.get_users_clubs(userId=userId)["message"]

        clubCommunications = []
        for clubId in usersClubs:
            clubsCommunications = CommunicationsModelTable.get_clubs_communications(clubId=clubId)["message"]
            clubsCommunications = [communication for communication in clubsCommunications if communication["status"]==1]
            
            clubsCommunications = [communication for communication in clubsCommunications if datetime.now()-datetime.strptime(communication["date"], "%Y-%m-%d")<timedelta(days=7)]
            if len(clubsCommunications)>0:
                communication = clubsCommunications[-1]
                communication["sender"] = UsersModelTable.get_officialName_from_userId(id=communication["senderId"])["message"]
                communication["club"] = ClubsModelTable.get_name_from_clubId(id=communication["clubId"])["message"]
                del communication["senderId"]
                del communication["clubId"]
                clubCommunications.append(clubsCommunications[-1])

        if len(clubCommunications)>10:
            clubCommunications = clubCommunications[:10]
        return jsonify(clubCommunications)
    else:
        return {}


def getUsersCommunications():
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="GET":
        officialName = request.officialName
        userId = UsersModelTable.get_userId_from_officialName(officialName=officialName)["message"]
        usersClubs = ClubMembershipsTable.get_users_clubs(userId=userId)["message"]

        clubCommunications = []
        for clubId in usersClubs:
            clubsCommunications = CommunicationsModelTable.get_clubs_communications(clubId=clubId)["message"]
            for communication in clubsCommunications:
                if communication["status"]==1:
                    communication["sender"] = UsersModelTable.get_officialName_from_userId(id=communication["senderId"])["message"]
                    communication["club"] = ClubsModelTable.get_name_from_clubId(id=communication["clubId"])["message"]
                    del communication["senderId"]
                    del communication["clubId"]
                    clubCommunications.append(communication)

        return jsonify(clubCommunications)
    else:
        return {}

def getAllCommunicationsAdmin():
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="GET":
        allCommunications = CommunicationsModelTable.get_all_communications()["message"]

        communications = []
        for communication in allCommunications:
            communication["clubName"] = ClubsModelTable.get_name_from_clubId(id=communication["clubId"])["message"]
            
            match communication["status"]:
                case -1: communication["status"] = "Denied"
                case 0: communication["status"] = "Pending"
                case 1: communication["status"] = "Sent"
            
            communication["sender"] = UsersModelTable.get_officialName_from_userId(communication["senderId"])["message"]
            del communication["senderId"]
            del communication["clubId"]

            communications.append(communication)

        return jsonify(communications)
    else:
        return {}


def approveCommunication(id):
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="PUT":
        updateMeetingStatus = CommunicationsModelTable.updateCommunicationStatus(id=id, status=1)["message"]
        return jsonify(updateMeetingStatus)
    else:
        return {}

def denyCommunication(id):
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="PUT":
        updateMeetingStatus = CommunicationsModelTable.updateCommunicationStatus(id=id, status=-1)["message"]
        return jsonify(updateMeetingStatus)
    else:
        return {}
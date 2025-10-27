import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import request
from flask import jsonify
from models import ClubsModel
from models import UsersModel
from models import ClubMembershipsModel
from models import ClubMeetingsModel
import numpy as np
import json
import os
from datetime import datetime

import os

# Ensure the database directory exists
db_dir = os.path.join(os.getcwd(), "database")
os.makedirs(db_dir, exist_ok=True)

# Use os.path.join for better cross-platform compatibility
db_path = os.path.join(db_dir, "TrinHubDB.db")

ClubsModelTable = ClubsModel.Club(db_name=db_path)
UsersModelTable = UsersModel.User(db_name=db_path)
ClubMembershipsTable = ClubMembershipsModel.ClubMemberships(db_name=db_path)
ClubMeetingsModelTable = ClubMeetingsModel.Meeting(db_name=db_path)


def getUserOfficialNameFromId(id):
    return UsersModelTable.get_officialName_from_userId(id)["message"]


def isLeader(officialName, clubName):
    clubId = ClubsModelTable.get_clubId_from_name(name=clubName)["message"]
    club = ClubsModelTable.get_club(id=clubId)["message"]

    userId = UsersModelTable.get_userId_from_officialName(officialName=officialName)["message"]

    if userId==club["facultyAdvisor"] or userId in club["studentLeaders"]:
        return True
    return False

def isMember(officialName, clubName):
    clubId = ClubsModelTable.get_clubId_from_name(name=clubName)["message"]
    clubMembers = ClubMembershipsTable.get_clubs_members(clubId)["message"]

    userId = UsersModelTable.get_userId_from_officialName(officialName=officialName)["message"]

    if userId in clubMembers:
        return True
    return False


# /clubs
def getClubs_createClub_deleteClub():
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="GET":
        clubs = ClubsModelTable.get_clubs()["message"]

        for club_index in range(len(clubs)):
            club = clubs[club_index]

            if club["facultyAdvisor"] != None:
                club["facultyAdvisor"] = getUserOfficialNameFromId(club["facultyAdvisor"])

            club["studentLeaders"] = [getUserOfficialNameFromId(studentLeaderId) for studentLeaderId in club["studentLeaders"]]

            club["memberCount"] = len(ClubMembershipsTable.get_clubs_members(clubId=club["id"])["message"])
            clubMeetings = ClubMeetingsModelTable.get_clubs_meetings(club_id=club["id"])["message"]
            sorted(clubMeetings, key=lambda x: float(int(x["date"].split("-")[0])+int(x["date"].split("-")[1])/12+int(x["date"].split("-")[2])/365))

            club["meetings"] = len(clubMeetings)
            club["quarterlyMeetings"] = [0,0,0,0,0,0,0]
            for meeting in clubMeetings:
                if meeting["status"]==1:
                    meetingDate = meeting['date'].split("-")
                    meetingDate = int(meetingDate[0][2:])*365+int(int(meetingDate[1])-1)*31+int(meetingDate[2])
                    quarters = [24*365+8*31+3, 24*365+9*30+31, 25*365+0*31+23, 25*365+2*31+14, 25*365+5*31+12]
                    if (meetingDate>=quarters[0] and meetingDate<=quarters[1]):
                        club["quarterlyMeetings"][0] += 1
                    if (meetingDate>=quarters[1] and meetingDate<=quarters[2]):
                        club["quarterlyMeetings"][1] += 1
                    if (meetingDate>=quarters[2] and meetingDate<=quarters[3]):
                        club["quarterlyMeetings"][3] += 1
                    if (meetingDate>=quarters[3] and meetingDate<=quarters[4]):
                        club["quarterlyMeetings"][4] += 1
                    club["quarterlyMeetings"][2] = club["quarterlyMeetings"][0]+club["quarterlyMeetings"][1]
                    club["quarterlyMeetings"][5] = club["quarterlyMeetings"][3]+club["quarterlyMeetings"][4]
                    club["quarterlyMeetings"][6] = club["quarterlyMeetings"][2]+club["quarterlyMeetings"][5]
                

            upcomingMeetings = []
            currentDate = datetime.today().strftime('%Y-%m-%d').split("-")
            currentDate = float(int(currentDate[0])+int(currentDate[1])/12+int(currentDate[2])/365)
            for meeting in clubMeetings:
                meetingDate = meeting["date"].split("-")
                numericalMeetingDate = float(float(meetingDate[0])+int(meetingDate[1])/12+int(meetingDate[2])/365)

                if numericalMeetingDate>=currentDate:
                    meeting["partialDate"] = str(int(meetingDate[1]))+"/"+str(int(meetingDate[2]))
                    meeting.update(time="("+meeting["startTime"]+"-"+meeting["endTime"]+")")
                    upcomingMeetings.append(meeting)
            upcomingMeetings=sorted(upcomingMeetings, key=lambda x: float(int(x["date"].split("-")[0])+int(x["date"].split("-")[1])/12+int(x["date"].split("-")[2])/365))
            
            club["nextMeeting"] = "NaN"
            if len(upcomingMeetings)!=0:
                club["nextMeeting"] = datetime.strptime(upcomingMeetings[0]["date"], "%Y-%m-%d").strftime("%m/%d/%y")


            clubs[club_index] = club

        return jsonify(clubs)
    elif request.method=="POST":
        data = request.json

        if data["facultyAdvisor"] != '':
            data["facultyAdvisor"] = UsersModelTable.get_userId_from_officialName(officialName=data["facultyAdvisor"])["message"]
        else:
            data["facultyAdvisor"] = None

        data["studentLeaders"] = [UsersModelTable.get_userId_from_officialName(officialName=studentLeaderName)["message"] for studentLeaderName in data["studentLeaders"]]
        
        createClub = ClubsModelTable.create_club(data)
        clubId = createClub["message"]["id"]

        for leaderId in data["studentLeaders"]:
            ClubMembershipsTable.add_user_to_club(userId=leaderId, clubId=clubId)

        return jsonify(createClub["message"])
    elif request.method=="DELETE":
        data = request.json
        deleteClub = ClubsModelTable.remove_club(name=data["clubName"])
        return jsonify(deleteClub["message"])
    else:
        return {}

def getClubs(): # This is for the admin view
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="GET":
        clubs = ClubsModelTable.get_clubs()["message"]

        return jsonify(clubs)
    else:
        return {}

def getJoinableClubs():
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="GET":
        clubs = ClubsModelTable.get_clubs()["message"]
        clubs = [club for club in clubs if club["acceptingMembers"]]
        return jsonify(clubs)
    else:
        return {}

def getClub(clubName):
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="GET":
        clubId = ClubsModelTable.get_clubId_from_name(name=clubName)["message"]
        club = ClubsModelTable.get_club(id=clubId)["message"]

        if club["facultyAdvisor"] != None:
            club["facultyAdvisor"] = getUserOfficialNameFromId(club["facultyAdvisor"])
        club["studentLeaders"] = [getUserOfficialNameFromId(studentLeaderId) for studentLeaderId in club["studentLeaders"]]

        return jsonify(club)
    else:
        return {}
    
def updateClub():
    if request.method=="PUT":
        data = request.json

        data['id'] = ClubsModelTable.get_clubId_from_name(data["clubName"])["message"]

        if data["facultyAdvisor"] != '':
            data["facultyAdvisor"] = UsersModelTable.get_userId_from_officialName(officialName=data["facultyAdvisor"])["message"]
        else:
            data["facultyAdvisor"] = None

        data["studentLeaders"] = [UsersModelTable.get_userId_from_officialName(officialName=studentLeaderName)["message"] for studentLeaderName in data["studentLeaders"]]

        updateClub = ClubsModelTable.update_club(data)
        clubId = updateClub["message"]

        for leaderId in data["studentLeaders"]:
            ClubMembershipsTable.add_user_to_club(userId=leaderId, clubId=clubId)

        return jsonify(updateClub["message"])
    else:
        return {}

def mailerGetUsersClub(officialName):
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="GET":
        userId = UsersModelTable.get_userId_from_officialName(officialName=officialName)["message"]
        usersClubsIds = ClubMembershipsTable.get_users_clubs(userId=userId)["message"]
        usersClubs = [ClubsModelTable.get_club(id=id)["message"] for id in usersClubsIds]
        return jsonify(usersClubs)
    else:
        return {}

def getUsersClub():
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="GET":
        officialName = request.officialName
        userId = UsersModelTable.get_userId_from_officialName(officialName=officialName)["message"]
        usersClubsIds = ClubMembershipsTable.get_users_clubs(userId=userId)["message"]
        usersClubs = [ClubsModelTable.get_club(id=id)["message"] for id in usersClubsIds]
        return jsonify(usersClubs)
    else:
        return {}

def getClubsUserLeads():
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="GET":
        officialName = request.officialName
        userId = UsersModelTable.get_userId_from_officialName(officialName=officialName)["message"]
        usersClubsIds = ClubMembershipsTable.get_users_clubs(userId=userId)["message"]
        usersClubs = [ClubsModelTable.get_club(id=id)["message"] for id in usersClubsIds]

        clubNames = []
        for club in usersClubs:
            if userId in club["studentLeaders"]:
                memberIds = ClubMembershipsTable.get_clubs_members(clubId=club["id"])["message"]
                members = [UsersModelTable.get_officialName_from_userId(id=memberId)["message"] for memberId in memberIds]
                club.update(members=members)

                clubMeetings = ClubMeetingsModelTable.get_clubs_meetings(club_id=club["id"])["message"]
                upcomingMeetings = []
                currentDate = datetime.today().strftime('%Y-%m-%d').split("-")
                currentDate = float(int(currentDate[0])+int(currentDate[1])/12+int(currentDate[2])/365)
                for meeting in clubMeetings:
                    meetingDate = meeting["date"].split("-")
                    numericalMeetingDate = float(float(meetingDate[0])+int(meetingDate[1])/12+int(meetingDate[2])/365)

                    if numericalMeetingDate>=currentDate:
                        meeting["partialDate"] = str(int(meetingDate[1]))+"/"+str(int(meetingDate[2]))
                        meeting.update(time="("+meeting["startTime"]+"-"+meeting["endTime"]+")")
                        upcomingMeetings.append(meeting)
                upcomingMeetings=sorted(upcomingMeetings, key=lambda x: float(int(x["date"].split("-")[0])+int(x["date"].split("-")[1])/12+int(x["date"].split("-")[2])/365))
                
                club["nextMeeting"] = "NaN"
                if len(upcomingMeetings)!=0:
                    club["nextMeeting"] = datetime.strptime(upcomingMeetings[0]["date"], "%Y-%m-%d").strftime("%m/%d/%y")


                clubNames.append(club)

        return jsonify(clubNames)
    else:
        return {}

def getClubsMembers(clubName):
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="GET":

        clubId = ClubsModelTable.get_clubId_from_name(name=clubName)["message"]

        clubMemberIds = ClubMembershipsTable.get_clubs_members(clubId=clubId)["message"]

        clubMemberNames = []
        for id in clubMemberIds:
            officialName = getUserOfficialNameFromId(id)
            clubMemberNames.append(officialName)

        return jsonify(clubMemberNames)
    else:
        return {}

def getClubsBlockedMembers(clubName):
    if request.method == "OPTIONS":
        return '', 200
    elif request.method == "GET":

        clubId = ClubsModelTable.get_clubId_from_name(name=clubName)["message"]

        blockedMemberIds = ClubsModelTable.get_blocked_members(clubId=clubId)["message"]
        
        blockedMemberNames = []
        for id in blockedMemberIds:
            officialName = getUserOfficialNameFromId(id)
            blockedMemberNames.append(officialName)

        return jsonify(blockedMemberNames)
    else:
        return {}

def joinClub():
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="POST":
        data = request.json
        clubName = data['clubName'].replace("%20", " ")
        officialName = request.officialName

        clubId = ClubsModelTable.get_clubId_from_name(name=clubName)["message"]
        userId = UsersModelTable.get_userId_from_officialName(officialName=officialName)["message"]
        
        club = ClubsModelTable.get_club(id=clubId)["message"]
        if club["acceptingMembers"]==True:
            clubMembership = ClubMembershipsTable.add_user_to_club(userId=userId, clubId=clubId)
            return jsonify(clubMembership["message"])
        else:
            return jsonify({"Club not accepting new members"})
    else:
        return {}

def removeUserFromClub(clubName):
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="POST":
        data = request.json
        userName = data["removedUser"].replace("%20", " ")

        clubId = ClubsModelTable.get_clubId_from_name(name=clubName.replace("%20", " "))["message"]
        userId = UsersModelTable.get_userId_from_officialName(officialName=userName)["message"]
        
        clubMembership = ClubMembershipsTable.remove_user_from_club(userId=userId, clubId=clubId)
        return jsonify(clubMembership["message"])
    else:
        return {}

def blockMember(clubName):
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="POST":
        data = request.json
        userName = data["removedUser"].replace("%20", " ")

        clubId = ClubsModelTable.get_clubId_from_name(name=clubName.replace("%20", " "))["message"]
        userId = UsersModelTable.get_userId_from_officialName(officialName=userName)["message"]
        
        clubMembership = ClubMembershipsTable.remove_user_from_club(userId=userId, clubId=clubId)
        blockMember = ClubsModelTable.blockMember(userId=userId, clubId=clubId)
        print(blockMember)
        
        return jsonify(blockMember["message"])
    else:
        return {}

def unBlockMember(clubName):
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="POST":
        data = request.json
        userName = data["unblockedUser"].replace("%20", " ")

        clubId = ClubsModelTable.get_clubId_from_name(name=clubName.replace("%20", " "))["message"]
        userId = UsersModelTable.get_userId_from_officialName(officialName=userName)["message"]
        
        blockMember = ClubsModelTable.unBlockMember(userId=userId, clubId=clubId)
        print(blockMember)
        
        return jsonify(blockMember["message"])
    else:
        return {}

def leaveClub():
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="POST":
        data = request.json
        clubName = data['clubName'].replace("%20", " ")
        officialName = request.officialName

        clubId = ClubsModelTable.get_clubId_from_name(name=clubName)["message"]
        userId = UsersModelTable.get_userId_from_officialName(officialName=officialName)["message"]

        clubMembership = ClubMembershipsTable.remove_user_from_club(userId=userId, clubId=clubId)["message"]
        return jsonify(clubMembership)
    else:
        return {}
    
def updateClubDescription(clubName):
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="PUT":
        data = request.json

        updatedDescription = ClubsModelTable.update_description(name=clubName.replace("%20", " "), description=data["description"])
        return jsonify(updatedDescription)
    else:
        return {}

def updateClubPhoto(clubName):
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="PUT":
        data = request.json

        updatedDescription = ClubsModelTable.update_photo(name=clubName.replace("%20", " "), photo=data["photo"])
        return jsonify(updatedDescription)
    else:
        return {}

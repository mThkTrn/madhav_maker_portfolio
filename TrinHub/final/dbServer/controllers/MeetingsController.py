from flask import request
from flask import jsonify
from models import ClubsModel
from models import ClubMembershipsModel
from models import ClubMeetingsModel
from models import UsersModel
from datetime import datetime, timedelta

#for service account
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build

#for personal account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import os
import json
from datetime import datetime

# SERVICE_ACCOUNT_FILE = 'service_account.json'  # Replace with TrinLabs email credentials

# # Define the required scopes for Google Calendar API
# SCOPES = ['https://www.googleapis.com/auth/calendar']

ClubsModelTable = ClubsModel.Club(f"{os.getcwd()}/database/TrinHubDB.db")
ClubMeetingsModelTable = ClubMeetingsModel.Meeting(f"{os.getcwd()}/database/TrinHubDB.db")
UsersModelTable = UsersModel.User(f"{os.getcwd()}/database/TrinHubDB.db")
ClubMembershipsModelTable = ClubMembershipsModel.ClubMemberships(f"{os.getcwd()}/database/TrinHubDB.db")

colorsBG = ["bg-purple-200", "bg-blue-200", "bg-red-200", "bg-green-200"]
colors = ["purple", "blue", "red", "green"]

def dayDeltaConversion(day):
    if day==6:
        return 0
    else:
        return day+1

def is_date_in_current_week(date):
    today = datetime.now().date()
    start_of_week = today - timedelta(days=dayDeltaConversion(today.weekday()))  # Sunday
    end_of_week = start_of_week + timedelta(days=6)  # Saturday
    return start_of_week <= date <= end_of_week

def get_day_of_week(date_string):
    # Convert the string to a datetime object
    date_object = datetime.strptime(date_string, '%Y-%m-%d')
    # Get the day of the week (0 = Monday, 6 = Sunday)
    day_index = date_object.weekday()
    # Adjust the index to match your format (Sun = 0, Sat = 6)
    day_index = (day_index + 1) % 7
    # Day options
    days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    return days[day_index]

def createClubMeeting_deleteMeeting(clubName):
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="POST":
        data = request.json

        clubId = ClubsModelTable.get_clubId_from_name(name=clubName)["message"]

        data.update(clubId=clubId)

        createMeeting = ClubMeetingsModelTable.create_meeting(meeting_details=data)["message"]

        send_google_calendar(meeting=data)


        return jsonify(createMeeting)
    elif request.method=="DELETE":
        data = request.json
        id = data["id"]
        clubId = ClubsModelTable.get_clubId_from_name(name=clubName)["message"]
        deletedMeeting = ClubMeetingsModelTable.delete_meeting(clubId, id)
        return jsonify(deletedMeeting)
    else:
        return {}

def getUpcomingMeetings(clubName):
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="GET":
        currentDate = datetime.today().strftime('%Y-%m-%d').split("-")
        currentDate = float(int(currentDate[0])+int(currentDate[1])/12+int(currentDate[2])/365)
        clubId = ClubsModelTable.get_clubId_from_name(name=clubName)["message"]

        clubsMeetings = ClubMeetingsModelTable.get_clubs_meetings(club_id=clubId)["message"]

        upcomingMeetings = []
        for meeting in clubsMeetings:
            meetingDate = meeting["date"].split("-")
            numericalMeetingDate = float(float(meetingDate[0])+int(meetingDate[1])/12+int(meetingDate[2])/365)

            if numericalMeetingDate>=currentDate:
                meeting["partialDate"] = str(int(meetingDate[1]))+"/"+str(int(meetingDate[2]))
                meeting.update(time="("+meeting["startTime"]+"-"+meeting["endTime"]+")")
                upcomingMeetings.append(meeting)
        upcomingMeetings=sorted(upcomingMeetings, key=lambda x: float(int(x["date"].split("-")[0])+int(x["date"].split("-")[1])/12+int(x["date"].split("-")[2])/365))

        return jsonify(upcomingMeetings)
    else:
        return {}

def attendMeeting():
    if request.method=="OPTIONS":
        return '', 200
    elif request.method == "POST":
        data = request.json

        idHash = data["idHash"]
        officialName = data["officialName"]
        clubName = data["clubName"]

        clubId = ClubsModelTable.get_clubId_from_name(name=clubName)["message"]
        userId = UsersModelTable.get_userId_from_officialName(officialName=officialName)["message"]

        usersClubs = ClubMembershipsModelTable.get_users_clubs(userId=userId)["message"]
        if clubId in usersClubs:
            attendMeeting = ClubMeetingsModelTable.attend_meeting(idHash=idHash, clubId=clubId, userId=userId, is_member=False)["message"]
            return jsonify(attendMeeting)
        else:
            attendMeeting = ClubMeetingsModelTable.attend_meeting(idHash=idHash, clubId=clubId, userId=userId, is_member=False)["message"]
            return jsonify(attendMeeting)

    else:
        return {}

def unattendMeeting():
    if request.method=="OPTIONS":
        return '', 200
    elif request.method == "POST":
        data = request.json

        idHash = data["idHash"]
        officialName = data["officialName"]
        clubName = data["clubName"]

        clubId = ClubsModelTable.get_clubId_from_name(name=clubName)["message"]
        userId = UsersModelTable.get_userId_from_officialName(officialName=officialName)["message"]

        usersClubs = ClubMembershipsModelTable.get_users_clubs(userId=userId)["message"]
        if clubId in usersClubs:
            attendMeeting = ClubMeetingsModelTable.remove_member_from_meeting(idHash=idHash, clubId=clubId, userId=userId)["message"]
            return jsonify(attendMeeting)
        else:
            attendMeeting = ClubMeetingsModelTable.remove_nonMember_from_meeting(idHash=idHash, clubId=clubId, userId=userId)["message"]
            return jsonify(attendMeeting)

    else:
        return {}


def getAllMeetings():
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="GET":
        allMeetings = ClubMeetingsModelTable.get_all_meetings()["message"]

        meetings = []
        for meeting in allMeetings:
            meeting["clubName"] = ClubsModelTable.get_name_from_clubId(id=meeting["clubId"])["message"]
            if int(meeting["status"])==1 and int(meeting["visibility"])==1:
                meeting["color"] = meeting["clubId"] % 4
                meeting["day"] = get_day_of_week(meeting["date"])
                meeting["time"] = meeting["startTime"]+"-"+meeting["endTime"]
                meeting["clubName"] = ClubsModelTable.get_name_from_clubId(meeting["clubId"])["message"]
                meetings.append(meeting)

        return jsonify(meetings)
    else:
        return {}


def getUsersMeetings():
    # THIS DOESNT WORK AT ALL
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="GET":
        officialName = request.officialName
        userId = UsersModelTable.get_userId_from_officialName(officialName=officialName)["message"]
        usersClubs = ClubMembershipsModelTable.get_users_clubs(userId=userId)["message"]

        meetings = []
        for meeting in usersClubs:
            meeting["clubName"] = ClubsModelTable.get_name_from_clubId(id=meeting["clubId"])["message"]
            meetings.append(meeting)

        return jsonify(meetings)
    else:
        return {}

def getWeeksMeetings():
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="GET":
        officialName = request.officialName
        userId = UsersModelTable.get_userId_from_officialName(officialName=officialName)["message"]
        usersClubs = ClubMembershipsModelTable.get_users_clubs(userId=userId)["message"]

        meetings = []
        for clubId in usersClubs:
            clubsMeetings = ClubMeetingsModelTable.get_clubs_meetings(club_id=clubId)["message"]
            for meeting in clubsMeetings:
                if meeting["status"]==1:
                    if is_date_in_current_week(datetime.strptime(meeting["date"], "%Y-%m-%d").date()):
                        meeting["color"] = clubId % 4
                        meeting["day"] = get_day_of_week(meeting["date"])
                        meeting["time"] = meeting["startTime"]+"-"+meeting["endTime"]
                        meeting["clubName"] = ClubsModelTable.get_name_from_clubId(clubId)["message"]
                        meetings.append(meeting)

        return jsonify(meetings)
    else:
        return {}

def getAllUserMeetings():
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="GET":
        officialName = request.officialName
        userId = UsersModelTable.get_userId_from_officialName(officialName=officialName)["message"]
        usersClubs = ClubMembershipsModelTable.get_users_clubs(userId=userId)["message"]

        meetings = []
        for clubId in usersClubs:
            clubsMeetings = ClubMeetingsModelTable.get_clubs_meetings(club_id=clubId)["message"]
            for meeting in clubsMeetings:
                if meeting["status"]==1:
                    meeting["color"] = clubId % 4
                    meeting["clubName"] = ClubsModelTable.get_name_from_clubId(clubId)["message"]
                    meetings.append(meeting)

        return jsonify(meetings)
    else:
        return {}

def getAllMeetingsAdmin():
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="GET":
            allMeetings = ClubMeetingsModelTable.get_all_meetings()["message"]

            currentDate = datetime.today().strftime('%Y-%m-%d').split("-")
            currentDate = float(int(currentDate[0])+int(currentDate[1])/12+int(currentDate[2])/365)

            meetings = []
            for meeting in allMeetings:
                meeting["clubName"] = ClubsModelTable.get_name_from_clubId(id=meeting["clubId"])["message"]
                
                match meeting["status"]:
                    case 0: meeting["status"]="Pending"
                    case 1: meeting["status"]="Approved"
                    case -1: meeting["status"]="Denied"
                
                meetingDate = meeting["date"].split("-")
                numericalMeetingDate = float(float(meetingDate[0])+int(meetingDate[1])/12+int(meetingDate[2])/365)

                if numericalMeetingDate<currentDate:
                    meeting["status"]="Elapsed"
                
                meeting["dateTime"] = meeting["date"]+", "+meeting["startTime"]+"-"+meeting["endTime"]

                del meeting["startTime"]
                del meeting["endTime"]
                del meeting["date"]
                del meeting["clubId"]
                del meeting["notPartOfClub"]
                del meeting["partOfClub"]
                meetings.append(meeting)
            return jsonify(meetings)
    else:
        return {}


def send_google_calendar(meeting):
    """
    Sends a Google Calendar invite for a given meeting to all members of the club.

    Args:
        meeting (dict): The meeting details containing 'title', 'location', 'description', 'date', 'startTime', 'endTime', and 'clubId'.

    Returns:
        None
    """
    # Step 1: Retrieve all members of the club using the `clubId`
    club_id = meeting['clubId']
    club_members_response = ClubMembershipsModelTable.get_clubs_members(clubId=club_id)
    
    if club_members_response["result"] != "success":
        print(f"Error retrieving club members: {club_members_response['message']}")
        return

    member_ids = club_members_response["message"]
    club_members_emails = []

    # Step 2: Retrieve email addresses of the members
    for user_id in member_ids:
        user_response = UsersModelTable.get_user(id=user_id)
        if user_response["result"] == "success" and user_response["message"]:
            club_members_emails.append(user_response["message"]["email"])

    if not club_members_emails:
        print(f"No members found for club ID: {club_id}")
        return

    # Step 3: Build meeting details
    start_time_iso = f"{meeting['date']}T{meeting['startTime']}:00-04:00"
    end_time_iso = f"{meeting['date']}T{meeting['endTime']}:00-04:00"
    event_payload = {
        'summary': meeting['title'],
        'location': meeting['location'],
        'description': meeting.get('description', 'No description'),
        'start': {'dateTime': start_time_iso, 'timeZone': 'America/New_York'},
        'end': {'dateTime': end_time_iso, 'timeZone': 'America/New_York'},
        'attendees': [{'email': email} for email in club_members_emails],
        'organizer': {'email': 'madhavendra.thakur26@trinityschoolnyc.org'},
    }

   
    try:
         # Step 4: Use service account credentials to access the Google Calendar API
        # # Load credentials
        # credentials = service_account.Credentials.from_service_account_file(
        #     os.path.join(os.path.dirname(__file__), 'service_account.json'),  # Update this path if necessary
        #     scopes=['https://www.googleapis.com/auth/calendar']
        # )
        # service = build('calendar', 'v3', credentials=credentials)

        # # Create the event
        # event = service.events().insert(calendarId='primary', body=event_payload, sendUpdates='all').execute()

        # Step 4: Use OAuth 2.0 to authenticate a user (deleted credentials, wait until we get a service account)
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        
        # Load credentials from the OAuth 2.0 client secrets file
        flow = InstalledAppFlow.from_client_secrets_file(os.path.join(os.path.dirname(__file__), 'user_account_credentials.json'), SCOPES)
        creds = flow.run_local_server(port=3030)  # Opens a browser for authentication

        service = build('calendar', 'v3', credentials=creds)

        # Create the event
        event = service.events().insert(calendarId='primary', body=event_payload, sendUpdates='all').execute()
        print(f"Event created successfully: {event.get('htmlLink')}")
        
        print(f"Event created successfully: {event.get('htmlLink')}")
    except Exception as e:
        print(f"Failed to create Google Calendar event: {e}")


def approveMeeting(id):
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="PUT":
        updateMeetingStatus = ClubMeetingsModelTable.updateMeetingStatus(id=id, status=1)["message"]
        return jsonify(updateMeetingStatus)
    else:
        return {}

def denyMeeting(id):
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="PUT":
        updateMeetingStatus = ClubMeetingsModelTable.updateMeetingStatus(id=id, status=-1)["message"]
        return jsonify(updateMeetingStatus)
    else:
        return {}


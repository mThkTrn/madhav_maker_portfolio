from flask import Flask, request, jsonify
from flask_cors import CORS
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import os
import sys
import json
from datetime import datetime


# Load keys from config/keys.json
config_path = os.path.join(os.path.dirname(__file__), 'config', 'keys.json')
with open(config_path, 'r') as f:
    keys = json.load(f)
GOOGLE_CLIENT_ID = keys['client_id']
INTERNAL_PASSWORD = keys['internal_password']

admins = ["deirdre.williamson@trinityschoolnyc.org", "caren.fall@trinityschoolnyc.org", "daniel.iofin26@trinityschoolnyc.org", "nicholas.hutfilz25@trinityschoolnyc.org", "madhavendra.thakur26@trinityschoolnyc.org"] # Remove student names in production
developers = ["justin.gohde@trinityschoolnyc.org", "daniel.iofin26@trinityschoolnyc.org", "nicholas.hutfilz25@trinityschoolnyc.org", "madhavendra.thakur26@trinityschoolnyc.org"] # Update to be on a need to know basis in production

# Set up paths for controllers and models
fpath = os.path.join(os.path.dirname(__file__), 'controllers')
sys.path.append(fpath)
fpath = os.path.join(os.path.dirname(__file__), 'models')
sys.path.append(fpath)

from controllers import ClubsController, MeetingsController, UsersController, AnalyticsController, CommunicationsController, DataController
from models import AnalyticsModel
AnalyticsModelTable = AnalyticsModel.Analytics(f"{os.getcwd()}/database/TrinHubDB.db")

app = Flask(__name__, static_url_path='', static_folder='static')
CORS(app)

def officialNameFromEmail(email):
    nameList = email.split("@")[0].split(".")
    name = nameList[0].capitalize()+" "+nameList[1].capitalize()
    name = ''.join([char for char in name if not char.isdigit()])
    return name

# Function to verify Google OAuth token
def verify_auth_token(token):
    try:
        # Verify the token
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), GOOGLE_CLIENT_ID)

        # If the token is valid, return the user's Google ID and email
        user_id = idinfo['sub']
        user_email = idinfo['email']
        return user_id, user_email
    except ValueError as e:
        # Invalid token
        return None, None

def verify_internal_password(token):
    try:
        # Verify the password
        if token==INTERNAL_PASSWORD:
            return True, "daniel.iofin26@trinityschoolnyc.org" #user_id, user_email
        else:
            return None, None
    except ValueError as e:
        # Invalid token
        return None, None

# Middleware for authentication
def authenticate_request():
    token = request.headers.get('Authorization')

    if token and token.startswith("Bearer "):
        token = token.split(" ")[1]  # Remove "Bearer " prefix
        user_id, user_email = verify_auth_token(token)
        if user_id:
            return user_id, user_email
    elif token and token.startswith("Internal ") and request.path.startswith("/api/internal"):
        token = token.split(" ")[1]  # Remove "Internal " prefix
        user_id, user_email = verify_internal_password(token)
        return user_id, user_email
    return None, None

# Check authentication before request is processed
@app.before_request
def before_request():
    request.startTime = datetime.now()
    # Skip token verification for non-API routes like static files
    if request.path=="/api/user/handleLogin":
        pass
    elif request.path.startswith("/api") and request.method!="OPTIONS":

        user_id, user_email = authenticate_request()
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401
        request.user_email = user_email
        request.officialName = officialNameFromEmail(user_email)
    
        if request.path.startswith("/api/admin"):
            if user_email not in admins:
                return jsonify({"error": "Unauthorized"}), 401
        elif request.path.startswith("/api/developer"):
            if user_email not in developers:
                return jsonify({"error": "Unauthorized"}), 401
        elif request.path.startswith("/api/clubLeader/"):
            if not ClubsController.isLeader(request.officialName, request.view_args.get("clubName")) and user_email not in admins:
                return jsonify({"error": "Unauthorized"}), 401
        elif request.path.startswith("/api/club/"):
            if not ClubsController.isMember(request.officialName, request.view_args.get("clubName")) and user_email not in admins:
                return jsonify({"error": "Unauthorized"}), 401


@app.teardown_request
def logAnalyticsEvent(response):
    elapsed = datetime.now()-request.startTime
    analyticsObject = {"method": request.method,
                    "url": request.path,
                    "startTime": request.startTime,
                    "elapsed": elapsed.total_seconds()}
    AnalyticsModelTable.log_event(event_details=analyticsObject)["message"]



# ------Register API routes------

# Internal routes (When possible, these routes should mimic other routes but with an internal prefix in the route)
app.add_url_rule('/api/internal/user/clubs/<officialName>', view_func=ClubsController.mailerGetUsersClub, methods=['GET'])
app.add_url_rule('/api/internal/club/meetings/<clubName>', view_func=MeetingsController.getUpcomingMeetings, methods=['GET'])
app.add_url_rule('/api/internal/club/communication/<clubName>', view_func=CommunicationsController.getClubCommunications, methods=['GET'])
app.add_url_rule('/api/internal/clubs/all', view_func=ClubsController.getClubs, methods=['GET'])
app.add_url_rule('/api/internal/users/all', view_func=UsersController.getUsers, methods=['GET'])

# Developer routes
app.add_url_rule('/api/developer/data/download', view_func=DataController.downloadDB, methods=['GET'])
app.add_url_rule('/api/developer/analytics', view_func=AnalyticsController.getAnalytics_processRequest, methods=['GET', 'POST'])

# School admin routes
app.add_url_rule('/api/admin/users/faculty', view_func=UsersController.getFaculty, methods=['GET'])
app.add_url_rule('/api/admin/users/currentStudents', view_func=UsersController.getCurrentStudents, methods=['GET'])
app.add_url_rule('/api/admin/users/all', view_func=UsersController.getUsers, methods=['GET', 'POST'])
app.add_url_rule('/api/admin/clubs/all', view_func=ClubsController.getClubs_createClub_deleteClub, methods=['GET', 'POST', 'PUT', 'DELETE'])
app.add_url_rule('/api/admin/meetings', view_func=MeetingsController.getAllMeetingsAdmin, methods=['GET'])
app.add_url_rule('/api/admin/communications', view_func=CommunicationsController.getAllCommunicationsAdmin, methods=['GET'])
app.add_url_rule('/api/admin/meeting/<id>/approve', view_func=MeetingsController.approveMeeting, methods=['PUT'])
app.add_url_rule('/api/admin/meeting/<id>/deny', view_func=MeetingsController.denyMeeting, methods=['PUT'])
app.add_url_rule('/api/admin/communication/<id>/approve', view_func=CommunicationsController.approveCommunication, methods=['PUT'])
app.add_url_rule('/api/admin/communication/<id>/deny', view_func=CommunicationsController.denyCommunication, methods=['PUT'])
app.add_url_rule('/api/admin/club/update', view_func=ClubsController.updateClub, methods=['PUT'])

# Clubs routes
app.add_url_rule('/api/clubs/joinable', view_func=ClubsController.getJoinableClubs, methods=['GET'])

# User routes
app.add_url_rule('/api/user/handleLogin', view_func=UsersController.handleLogin, methods=['POST'])
app.add_url_rule('/api/user', view_func=UsersController.getUser_updateUser_deleteUser, methods=['GET', 'DELETE'])
app.add_url_rule('/api/user/clubs', view_func=ClubsController.getUsersClub, methods=['GET'])
app.add_url_rule('/api/user/clubs/leader', view_func=ClubsController.getClubsUserLeads, methods=['GET'])
app.add_url_rule('/api/user/communications/latest', view_func=CommunicationsController.getLatestUsersCommunications, methods=['GET'])
app.add_url_rule('/api/user/communications', view_func=CommunicationsController.getUsersCommunications, methods=['GET'])
app.add_url_rule('/api/user/meetings/week', view_func=MeetingsController.getWeeksMeetings, methods=['GET'])
app.add_url_rule('/api/user/meetings/all', view_func=MeetingsController.getAllMeetings, methods=['GET'])
app.add_url_rule('/api/user/meetings', view_func=MeetingsController.getAllUserMeetings, methods=['GET'])
app.add_url_rule('/api/user/meeting/attend', view_func=MeetingsController.attendMeeting, methods=['POST'])
app.add_url_rule('/api/user/meeting/unattend', view_func=MeetingsController.unattendMeeting, methods=['POST'])
app.add_url_rule('/api/user/club/join', view_func=ClubsController.joinClub, methods=['POST'])
app.add_url_rule('/api/user/club/leave', view_func=ClubsController.leaveClub, methods=['POST'])

# Club routes
app.add_url_rule('/api/club/<clubName>', view_func=ClubsController.getClub, methods=['GET'])
app.add_url_rule('/api/club/<clubName>/meetings/upcoming', view_func=MeetingsController.getUpcomingMeetings, methods=['GET'])
app.add_url_rule('/api/club/<clubName>/communications', view_func=CommunicationsController.getClubCommunications, methods=['GET'])

# Club leader routes
app.add_url_rule('/api/clubLeader/<clubName>/updateDescription', view_func=ClubsController.updateClubDescription, methods=['PUT'])
app.add_url_rule('/api/clubLeader/<clubName>/updatePhoto', view_func=ClubsController.updateClubPhoto, methods=['PUT'])
app.add_url_rule('/api/clubLeader/<clubName>/communication', view_func=CommunicationsController.createClubCommunication_updateClubCommunication_deleteClubCommunication, methods=['POST', 'PUT', 'DELETE'])
app.add_url_rule('/api/clubLeader/<clubName>/members', view_func=ClubsController.getClubsMembers, methods=['GET'])
app.add_url_rule('/api/clubLeader/<clubName>/blocked', view_func=ClubsController.getClubsBlockedMembers, methods=['GET'])
app.add_url_rule('/api/clubLeader/<clubName>/member/remove', view_func=ClubsController.removeUserFromClub, methods=['POST'])
app.add_url_rule('/api/clubLeader/<clubName>/member/block', view_func=ClubsController.blockMember, methods=['POST'])
app.add_url_rule('/api/clubLeader/<clubName>/member/unblock', view_func=ClubsController.unBlockMember, methods=['POST'])
app.add_url_rule('/api/clubLeader/<clubName>/meetings', view_func=MeetingsController.createClubMeeting_deleteMeeting, methods=['POST', 'DELETE'])


# Run the Flask app
app.run(debug=True, port=3001)

import os
from models import ClubMeetingsModel, ClubMembershipsModel, ClubsModel, UsersModel, AnalyticsModel, CommunicationsModel
import sqlite3


databaseDirectory = os.getcwd()+"/database"
print("Database directory is: "+databaseDirectory+"\n")

databaseName = "TrinHubDB"
databasePath = f"{databaseDirectory}/{databaseName}.db"


# Analytics db
print(AnalyticsModel.Analytics(databasePath).initialize_analytics_table())
# Club meetings db
print(ClubMeetingsModel.Meeting(databasePath).initialize_meetings_table())
# Club communications db
print(CommunicationsModel.Communications(databasePath).initialize_communications_table())
# Club memberships db
print(ClubMembershipsModel.ClubMemberships(databasePath).initialize_clubMemberships_table())
# Clubs db
print(ClubsModel.Club(databasePath).initialize_clubs_table())
# Users db
print(UsersModel.User(databasePath).initialize_users_table())
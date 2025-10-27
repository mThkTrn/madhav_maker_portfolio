from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import random
import json
import os

def data_to_dict(meeting):
    return {key: getattr(meeting, key) for key in ["id", "clubId", "title", "date", "startTime", "endTime", "adHocMeeting", "location", "visibility", "partOfClub", "notPartOfClub", "status"]}

Base = declarative_base()

class MeetingModel(Base):
    __tablename__ = 'meetings'
    
    id = Column(Integer, primary_key=True)
    clubId = Column(Integer)
    title = Column(String)
    date = Column(String)
    startTime = Column(String)
    endTime = Column(String)
    adHocMeeting = Column(Boolean)
    location = Column(String)
    visibility = Column(String)
    partOfClub = Column(Text)  # Stores JSON strings for partOfClub
    notPartOfClub = Column(Text)  # Stores JSON strings for notPartOfClub
    status = Column(Integer, default=0)


class Meeting:
    def __init__(self, db_name):
        engine_url = os.getenv('DATABASE_URL')
        self.engine = create_engine(engine_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def initialize_meetings_table(self):
        # Create a new session
        session = self.Session()
        try:
            # Delete all data in the analytics table
            session.execute(text("DELETE FROM meetings"))  # Replace with your actual table name
            session.commit()
            return {"result": "success", "message": "All data deleted and table initialized"}
        except Exception as e:
            session.rollback()
            return {"result": "error", "message": str(e)}
        finally:
            session.close()

    def getAllData(self):
        session = self.Session()
        try:
            meetings = session.query(MeetingModel).all()
            return {"result": "success", "message": [data_to_dict(meeting) for meeting in meetings]}

        except SQLAlchemyError as error:
            return {"result": "error", "message": str(error)}

        finally:
            session.close()

    def create_meeting(self, meeting_details=None):
        session = self.Session()
        try:
            if meeting_details is None:
                return {"result": "error", "message": "noDataSupplied"}

            meeting_id = random.randint(0, 9007199254740991)

            if "title" not in meeting_details:
                meeting_details["title"] = ""

            new_meeting = MeetingModel(
                id=meeting_id,
                clubId=meeting_details["clubId"],
                title=meeting_details["title"],
                date=meeting_details["date"],
                startTime=meeting_details["startTime"],
                endTime=meeting_details["endTime"],
                adHocMeeting=meeting_details["adHocMeeting"],
                location=meeting_details["location"],
                visibility=meeting_details["visibility"],
                partOfClub=json.dumps([]),
                notPartOfClub=json.dumps([])
            )

            session.add(new_meeting)
            session.commit()

            return {"result": "success", "message": data_to_dict(new_meeting)}
        except SQLAlchemyError as error:
            session.rollback()
            print(error)
            return {"result": "error", "message": str(error)}
        finally:
            session.close()

    def get_clubs_meetings(self, club_id=None):
        session = self.Session()
        try:
            if club_id is None:
                return {"result": "error", "message": "noDataSupplied"}

            meetings = session.query(MeetingModel).filter_by(clubId=club_id).all()
            return {"result": "success", "message": [data_to_dict(meeting) for meeting in meetings]}
        except SQLAlchemyError as error:
            return {"result": "error", "message": str(error)}
        finally:
            session.close()

    def get_all_meetings(self):
        session = self.Session()
        try:
            meetings = session.query(MeetingModel).all()
            return {"result": "success", "message": [data_to_dict(meeting) for meeting in meetings]}
        except SQLAlchemyError as error:
            return {"result": "error", "message": str(error)}
        finally:
            session.close()

    def attend_meeting(self, idHash=None, clubId=None, userId=None, is_member=False):
        session = self.Session()
        try:
            if idHash is None or clubId is None or userId is None:
                return {"result": "error", "message": "noDataSupplied"}

            meeting = session.query(MeetingModel).filter_by(id=idHash, clubId=clubId).first()
            if meeting:
                if is_member:
                    attendingList = json.loads(meeting.partOfClub)
                    if userId not in attendingList:
                        attendingList.append(userId)
                        meeting.partOfClub = json.dumps(attendingList)
                        session.commit()
                        return {"result": "success", "message": "memberAddedToMeetingSuccessfully"}
                else:
                    attendingList = json.loads(meeting.notPartOfClub)
                    if userId not in attendingList:
                        attendingList.append(userId)
                        meeting.notPartOfClub = json.dumps(attendingList)
                        session.commit()
                        return {"result": "success", "message": "nonMemberAddedToMeetingSuccessfully"}

            return {"result": "error", "message": "matchingMeetingNotFound"}
        except SQLAlchemyError as error:
            session.rollback()
            return {"result": "error", "message": str(error)}
        finally:
            session.close()


    def remove_member_from_meeting(self, idHash=None, clubId=None, userId=None, is_member=True):
        session = self.Session()
        try:
            if idHash is None or clubId is None or userId is None:
                return {"result": "error", "message": "noDataSupplied"}

            meeting = session.query(MeetingModel).filter_by(id=idHash, clubId=clubId).first()
            if meeting:
                members_list = json.loads(meeting.partOfClub if is_member else meeting.notPartOfClub)
                if userId in members_list:
                    members_list.remove(userId)
                    if is_member:
                        meeting.partOfClub = json.dumps(members_list)
                    else:
                        meeting.notPartOfClub = json.dumps(members_list)
                    session.commit()
                    return {"result": "success", "message": "memberRemovedFromMeetingSuccessfully"}

            return {"result": "error", "message": "matchingMeetingNotFound"}
        except SQLAlchemyError as error:
            session.rollback()
            return {"result": "error", "message": str(error)}
        finally:
            session.close()
    
    def updateMeetingStatus(self, id=None, status=None):
        session = self.Session()
        try:
            if status is None or id is None:
                return {"result": "error", "message": "noDataSupplied"}
            meeting = session.query(MeetingModel).filter_by(id=id).first()
            if meeting:
                meeting.status = status
                session.commit()
                return {"result": "success", "message": "meetingStatusUpdated"}
            else:
                return {"result": "error", "message": "meetingNotFound"}
        except SQLAlchemyError as error:
            session.rollback()
            return {"result": "error", "message": str(error)}
        finally:
            session.close()

    def delete_meeting(self, clubId=None, id=None):
        session = self.Session()
        try:
            if clubId is None or id is None:
                return {"result": "error", "message": "noDataSupplied"}

            meeting = session.query(MeetingModel).filter_by(id=id, clubId=clubId).first()
            if meeting:
                session.delete(meeting)
                session.commit()
                return {"result": "success", "message": "clubMeetingSuccessfullyDeleted"}

            return {"result": "error", "message": "meetingNotFound"}
        except SQLAlchemyError as error:
            session.rollback()
            return {"result": "error", "message": str(error)}
        finally:
            session.close()

from sqlalchemy import create_engine, Column, Integer, Table, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
import os

def data_to_dict(membership):
    return {key: getattr(membership, key) for key in ["clubId", "userId"]}

Base = declarative_base()

class ClubMembershipModel(Base):
    __tablename__ = 'clubMemberships'
    
    clubId = Column(Integer, primary_key=True)
    userId = Column(Integer, primary_key=True)


class ClubMemberships:
    def __init__(self, db_name):
        engine_url = os.getenv('DATABASE_URL')
        self.engine = create_engine(engine_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.table_name = "clubMemberships"

    def initialize_clubMemberships_table(self):
        # Create a new session
        session = self.Session()
        try:
            # Delete all data in the analytics table
            session.execute(text("DELETE FROM clubMemberships"))  # Replace with your actual table name
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
            clubMemberships = session.query(ClubMembershipModel).all()
            return {"result": "success", "message": [data_to_dict(clubMembership) for clubMembership in clubMemberships]}

        except SQLAlchemyError as error:
            return {"result": "error", "message": str(error)}

        finally:
            session.close()

    def add_user_to_club(self, userId=None, clubId=None):
        session = self.Session()
        try:
            if userId is None or clubId is None:
                return {"result": "success", "message": "NoDataSupplied"}

            membership = session.query(ClubMembershipModel).filter_by(clubId=clubId, userId=userId).first()

            if membership:
                return {"result": "success", "message": "UserAlreadyPartOfClub"}

            new_membership = ClubMembershipModel(clubId=clubId, userId=userId)
            session.add(new_membership)
            session.commit()

            return {"result": "success", "message": "UserAddedSuccessfully"}

        except SQLAlchemyError as error:
            session.rollback()
            return {"result": "error", "message": str(error)}

        finally:
            session.close()

    def get_users_clubs(self, userId=None):
        session = self.Session()
        try:
            if userId is None:
                return {"result": "success", "message": []}

            memberships = session.query(ClubMembershipModel.clubId).filter_by(userId=userId).all()
            club_ids = [club_id for (club_id,) in memberships]

            return {"result": "success", "message": club_ids}

        except SQLAlchemyError as error:
            return {"result": "error", "message": str(error)}

        finally:
            session.close()

    def get_clubs_members(self, clubId=None):
        session = self.Session()
        try:
            if clubId is None:
                return {"result": "success", "message": []}

            members = session.query(ClubMembershipModel.userId).filter_by(clubId=clubId).all()
            member_ids = [user_id for (user_id,) in members]

            return {"result": "success", "message": member_ids}

        except SQLAlchemyError as error:
            return {"result": "error", "message": str(error)}

        finally:
            session.close()

    def remove_user_from_club(self, userId=None, clubId=None):
        session = self.Session()
        try:
            if userId is None or clubId is None:
                return {"result": "success", "message": "NoDataSupplied"}

            membership = session.query(ClubMembershipModel).filter_by(clubId=clubId, userId=userId).first()

            if not membership:
                return {"result": "success", "message": "UserNotPartOfClub"}

            session.delete(membership)
            session.commit()

            return {"result": "success", "message": data_to_dict(membership)}

        except SQLAlchemyError as error:
            session.rollback()
            return {"result": "error", "message": str(error)}

        finally:
            session.close()

    def remove_club(self, clubId=None):
        session = self.Session()
        try:
            if clubId is None:
                return {"result": "success", "message": "NoDataSupplied"}

            memberships = session.query(ClubMembershipModel).filter_by(clubId=clubId).all()

            if not memberships:
                return {"result": "success", "message": "ClubAlreadyRemoved"}

            for membership in memberships:
                session.delete(membership)

            session.commit()
            return {"result": "success", "message": "ClubRemovedSuccessfully"}

        except SQLAlchemyError as error:
            session.rollback()
            return {"result": "error", "message": str(error)}

        finally:
            session.close()

    def remove_user(self, userId=None):
        session = self.Session()
        try:
            if userId is None:
                return {"result": "success", "message": "NoDataSupplied"}

            memberships = session.query(ClubMembershipModel).filter_by(userId=userId).all()

            if not memberships:
                return {"result": "success", "message": "UserAlreadyRemoved"}

            for membership in memberships:
                session.delete(membership)

            session.commit()
            return {"result": "success", "message": "UserRemovedSuccessfully"}

        except SQLAlchemyError as error:
            session.rollback()
            return {"result": "error", "message": str(error)}

        finally:
            session.close()

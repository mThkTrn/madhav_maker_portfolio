from sqlalchemy import create_engine, Column, Integer, String, DateTime, func, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
import random
from datetime import datetime
import os

def data_to_dict(communication):
    return {key: getattr(communication, key) for key in ["id", "clubId", "senderId", "date", "dateTime", "subject", "message", "status"]}


Base = declarative_base()

class Communication(Base):
    __tablename__ = 'communications'

    id = Column(Integer, primary_key=True)
    clubId = Column(Integer, nullable=False)
    senderId = Column(Integer, nullable=False)
    date = Column(String, nullable=False)
    dateTime = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    message = Column(String, nullable=False)
    status = Column(Integer, default=0)

# Database handler class
class Communications:
    def __init__(self, db_name):
        engine_url = os.getenv('DATABASE_URL')
        self.engine = create_engine(engine_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def initialize_communications_table(self):
        # Create a new session
        session = self.Session()
        try:
            # Delete all data in the analytics table
            session.execute(text("DELETE FROM communications"))  # Replace with your actual table name
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
            communications = session.query(Communication).all()
            return {"result": "success", "message": [data_to_dict(communication) for communication in communications]}

        except SQLAlchemyError as error:
            return {"result": "error", "message": str(error)}

        finally:
            session.close()

    def create_communication(self, communication_details=None):
        session = self.Session()
        try:
            
            if communication_details is None:
                return {"result": "error", "message": "noDataSupplied"}
            elif communication_details.get("clubId") is None or \
               communication_details.get("senderId") is None or \
               communication_details.get("subject") is None or \
               communication_details.get("message") is None:
                return {"result": "error", "message": "incompleteDataSupplied"}

            # Random ID generation (SQLite handles auto-increment, but keeping this for parity)
            id = random.randint(0, 9007199254740991)
            while session.query(Communication).filter_by(id=id).first():
                id = random.randint(0, 9007199254740991)
            
            new_communication = Communication(
                id=id,
                clubId=communication_details["clubId"],
                senderId=communication_details["senderId"],
                date=str(datetime.now().strftime('%Y-%m-%d')),
                dateTime=str(datetime.now().strftime('%Y-%m-%d %H:%M')),
                subject=communication_details["subject"],
                message=communication_details["message"]
            )

            session.add(new_communication)
            session.commit()
            return {"result": "success", "message": data_to_dict(new_communication)}

        except SQLAlchemyError as error:
            session.rollback()
            return {"result": "error", "message": str(error)}

        finally:
            session.close()

    def get_clubs_communications(self, clubId=None):
        session = self.Session()
        try:
            if clubId is None:
                return {"result": "error", "message": "noClubIdSupplied"}

            communications = session.query(Communication).filter_by(clubId=clubId).all()
            output = [data_to_dict(communication) for communication in communications]
            output = sorted(output, key=lambda communication: communication['date'])
            return {"result": "success", "message": output}

        except SQLAlchemyError as error:
            return {"result": "error", "message": str(error)}

        finally:
            session.close()

    def get_all_communications(self):
        session = self.Session()
        try:
            communications = session.query(Communication).all()
            return {"result": "success", "message": [data_to_dict(communication) for communication in communications]}
        except SQLAlchemyError as error:
            return {"result": "error", "message": str(error)}
        finally:
            session.close()

    def update_communication(self, id=None, message=None):
        session = self.Session()
        try:
            if id is None or message is None:
                return {"result": "error", "message": "noDataSupplied"}

            communication = session.query(Communication).filter_by(id=id).first()
            if not communication:
                return {"result": "error", "message": "communicationNotFound"}

            communication.message = message
            session.commit()
            return {"result": "success", "message": "communicationUpdated"}

        except SQLAlchemyError as error:
            session.rollback()
            return {"result": "error", "message": str(error)}

        finally:
            session.close()

    def updateCommunicationStatus(self, id=None, status=None):
            session = self.Session()
            try:
                if status is None or id is None:
                    return {"result": "error", "message": "noDataSupplied"}
                communication = session.query(Communication).filter_by(id=id).first()
                if communication:
                    communication.status = status
                    session.commit()
                    return {"result": "success", "message": "communicationStatusUpdated"}
                else:
                    return {"result": "error", "message": "communicationNotFound"}
            except SQLAlchemyError as error:
                session.rollback()
                return {"result": "error", "message": str(error)}
            finally:
                session.close()

    def delete_communication(self, id=None):
        session = self.Session()
        try:
            if id is None:
                return {"result": "error", "message": "noDataSupplied"}

            communication = session.query(Communication).filter_by(id=id).first()
            if not communication:
                return {"result": "error", "message": "communicationNotFound"}

            session.delete(communication)
            session.commit()
            return {"result": "success", "message": "communicationDeleted"}

        except SQLAlchemyError as error:
            session.rollback()
            return {"result": "error", "message": str(error)}

        finally:
            session.close()

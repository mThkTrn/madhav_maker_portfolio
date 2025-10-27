from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import random
from datetime import datetime
import os

def data_to_dict(analytics):
    return {key: getattr(analytics, key) for key in ["id", "method", "url", "timeInitiated", "elapsed"]}


Base = declarative_base()

class AnalyticsModel(Base):
    __tablename__ = 'analytics'
    
    id = Column(Integer, primary_key=True)
    method = Column(String)
    url = Column(String)
    timeInitiated = Column(DateTime)
    elapsed = Column(Float)


class Analytics:
    def __init__(self, db_name):
        engine_url = os.getenv('DATABASE_URL')
        self.engine = create_engine(engine_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def initialize_analytics_table(self):
        # Create a new session
        session = self.Session()
        try:
            # Delete all data in the analytics table
            session.execute(text("DELETE FROM analytics"))  # Replace with your actual table name
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
            analytics = session.query(AnalyticsModel).all()
            return {"result": "success", "message": [data_to_dict(analytic) for analytic in analytics]}

        except SQLAlchemyError as error:
            return {"result": "error", "message": str(error)}

        finally:
            session.close()

    def log_event(self, event_details=None):
        session = self.Session()
        try:
            if event_details is None:
                return {"result": "error", "message": "noDataSupplied"}

            new_event = AnalyticsModel(
                id=random.randint(0, 9007199254740991),
                method=event_details["method"],
                url=event_details["url"],
                timeInitiated=event_details["startTime"],
                elapsed=event_details["elapsed"]
            )
            session.add(new_event)
            session.commit()
            return {"result": "success", "message": new_event.id}

        except SQLAlchemyError as error:
            session.rollback()
            return {"result": "error", "message": str(error)}

        finally:
            session.close()

    def get_events(self):
        session = self.Session()
        try:
            events = session.query(AnalyticsModel).all()
            output = [data_to_dict(event) for event in events]
            return {"result": "success", "message": output}

        except SQLAlchemyError as error:
            return {"result": "error", "message": str(error)}

        finally:
            session.close()

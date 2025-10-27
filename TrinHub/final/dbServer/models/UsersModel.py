from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
import random
import os

Base = declarative_base()

def data_to_dict(user):
        return {key: getattr(user, key) for key in ["id", "email", "officialName", "preferredName"]}

# Define the User model
class UserModel(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    officialName = Column(String, unique=True, nullable=False)
    preferredName = Column(String, nullable=True)

# Database handler class
class User:
    def __init__(self, db_name):
        engine_url = os.getenv('DATABASE_URL')
        self.engine = create_engine(engine_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def initialize_users_table(self):
        # Create a new session
        session = self.Session()
        try:
            # Delete all data in the analytics table
            session.execute(text("DELETE FROM users"))  # Replace with your actual table name
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
            users = session.query(UserModel).all()
            return {"result": "success", "message": [data_to_dict(user) for user in users]}

        except SQLAlchemyError as error:
            return {"result": "error", "message": str(error)}

        finally:
            session.close()

    def create_user(self, user_details):
        session = self.Session()
        try:
            user_id = random.randint(0, 9007199254740991)

            # Check for valid Trinity email
            if "@trinityschoolnyc.org" not in user_details["email"]:
                return {"result": "error", "message": "Please enter a valid Trinity email"}

            # Check for duplicate email
            existing_user = session.query(UserModel).filter_by(email=user_details["email"]).first()
            if existing_user:
                return {"result": "error", "message": "An account for this email already exists"}

            new_user = UserModel(
                id=user_id,
                email=user_details["email"],
                officialName=user_details["officialName"],
                preferredName=user_details["preferredName"]
            )
            session.add(new_user)
            session.commit()
            return {"result": "success", "message": data_to_dict(new_user)}


        except SQLAlchemyError as error:
            session.rollback()
            return {"result": "error", "message": str(error)}

        finally:
            session.close()

    def exists(self, email=None):
        session = self.Session()
        try:
            if email:
                user = session.query(UserModel).filter_by(email=email).first()
                if user:
                    return {"result": "success", "message": True}
                return {"result": "success", "message": False}
            return {"result": "success", "message": "NoDataSupplied"}

        except SQLAlchemyError as error:
            return {"result": "error", "message": str(error)}

        finally:
            session.close()

    def get_userId_from_officialName(self, officialName=None):
        session = self.Session()
        if officialName:
            user = session.query(UserModel).filter(UserModel.officialName==officialName).first()
            session.close()
            user = data_to_dict(user)
            if user:
                return {"result": "success", "message": user['id']}
        return {"result": "success", "message": []}


    def get_officialName_from_userId(self, id=None):
        session = self.Session()
        try:
            if id:
                user = session.query(UserModel).filter(UserModel.id==id).first()
                if user:
                    return {"result": "success", "message": user.officialName}
            return {"result": "success", "message": []}

        except SQLAlchemyError as error:
            return {"result": "error", "message": str(error)}

        finally:
            session.close()

    def get_user(self, id=None, officialName=None):
        session = self.Session()
        try:
            if id:
                user = session.query(UserModel).filter_by(id=id).first()
                if user:
                    return {"result": "success", "message": data_to_dict(user)}
            elif officialName:
                user = session.query(UserModel).filter_by(officialName=officialName).first()
                if user:
                    return {"result": "success", "message": data_to_dict(user)}
            return {"result": "error", "message": {}}

        except SQLAlchemyError as error:
            return {"result": "error", "message": str(error)}

        finally:
            session.close()

    def get_users(self):
        session = self.Session()
        try:
            users = session.query(UserModel).all()
            return {"result": "success", "message": [data_to_dict(user) for user in users]}

        except SQLAlchemyError as error:
            return {"result": "error", "message": str(error)}

        finally:
            session.close()

    def remove_user(self, officialName=None):
        session = self.Session()
        try:
            if officialName:
                user = session.query(UserModel).filter_by(officialName=officialName).first()
                if user:
                    session.delete(user)
                    session.commit()
                    return {"result": "success", "message": data_to_dict(user)}
            return {"result": "error", "message": {}}

        except SQLAlchemyError as error:
            session.rollback()
            return {"result": "error", "message": str(error)}

        finally:
            session.close()

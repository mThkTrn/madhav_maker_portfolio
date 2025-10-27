from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
import random
import json
import os

Base = declarative_base()

def data_to_dict(club):
    club = {key: getattr(club, key) for key in ["id", "name", "type", "facultyAdvisor", "studentLeaders", "description", "image", "acceptingMembers", "blockedMembers"]}
    club["studentLeaders"] = json.loads(club["studentLeaders"])
    club["blockedMembers"] = json.loads(club["blockedMembers"])
    return club


class ClubModel(Base):
    __tablename__ = 'clubs'
    
    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String, unique=True, nullable=False)
    type = Column(String, nullable=False)
    facultyAdvisor = Column(Integer)
    studentLeaders = Column(String)
    description = Column(Text, default="Hmm... Seems like the club leaders haven't added a description yet...")
    image = Column(String, default="https://imgs.search.brave.com/QWSbLeA-S-SCjPWVpMAuR1EzHdCoVeP9nAxzyOmmatg/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9zdGF0/aWMudGltZXNvZmlz/cmFlbC5jb20vYmxv/Z3MvdXBsb2Fkcy8y/MDIwLzA2L2lzcmFl/bC1zdG9jay1waWN0/dXJlcy5qcGc")
    acceptingMembers = Column(Boolean, default=True)
    blockedMembers = Column(Text)

class Club:
    def __init__(self, db_name):
        engine_url = os.getenv('DATABASE_URL')
        self.engine = create_engine(engine_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def initialize_clubs_table(self):
        # Create a new session
        session = self.Session()
        try:
            # Delete all data in the analytics table
            session.execute(text("DELETE FROM clubs"))  # Replace with your actual table name
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
            clubs = session.query(ClubModel).all()
            return {"result": "success", "message": [data_to_dict(club) for club in clubs]}

        except SQLAlchemyError as error:
            return {"result": "error", "message": str(error)}

        finally:
            session.close()

    def create_club(self, club_details):
        session = self.Session()
        try:
            club_id = random.randint(0, 9007199254740991)  # non-negative range of SQLITE3 INTEGER
            existing_club = session.query(ClubModel).filter_by(name=club_details["name"]).first()

            if existing_club:
                return {"result": "error", "message": "NameTaken"}

            if club_details["type"] not in ["General", "Affinity", "Publication", "Forensic", "Performing Art", "Service"]:
                return {"result": "error", "message": "InvalidType"}
            
            imageURL = ""
            match club_details["type"]:
                case "General":
                    imageURL = "https://i.ibb.co/B3c7NK1/image13.jpg"
                case "Affinity":
                    imageURL = "https://i.ibb.co/MkgcLbJ/image5.jpg"
                case "Publication":
                    imageURL = "https://i.ibb.co/30NCXVb/image0.jpg"
                case "Forensic":
                    imageURL = "https://i.ibb.co/m5YG2NB/image8.jpg"
                case "Performing Art":
                    imageURL = "https://i.ibb.co/S5xw8Zy/image14.jpg"
                case "Service":
                    imageURL = "https://i.ibb.co/SyvggQY/image11.jpg"
                    
            club = ClubModel(
                id=club_id,
                name=club_details["name"],
                type=club_details["type"],
                facultyAdvisor=club_details.get("facultyAdvisor"),
                studentLeaders=json.dumps(club_details.get("studentLeaders")),
                image=imageURL,
                blockedMembers = json.dumps([])
            )
            session.add(club)
            session.commit()
            return {"result": "success", "message": data_to_dict(club)}

        except SQLAlchemyError as error:
            session.rollback()
            return {"result": "error", "message": str(error)}

        finally:
            session.close()

    def exists(self, name=None, id=None):
        session = self.Session()
        try:
            if name:
                club = session.query(ClubModel).filter_by(name=name).first()
                return {"result": "success", "message": bool(club)}

            if id:
                club = session.query(ClubModel).filter_by(id=id).first()
                return {"result": "success", "message": bool(club)}

            return {"result": "success", "message": "NoDataSupplied"}

        except SQLAlchemyError as error:
            return {"result": "error", "message": str(error)}

        finally:
            session.close()

    def get_club(self, name=None, id=None):
        session = self.Session()
        try:
            if name:
                club = session.query(ClubModel).filter_by(name=name).first()
            elif id:
                club = session.query(ClubModel).filter_by(id=id).first()
            else:
                return {"result": "success", "message": []}

            if club:
                return {"result": "success", "message": data_to_dict(club)}
            else:
                return {"result": "error", "message": {}}

        except SQLAlchemyError as error:
            return {"result": "error", "message": str(error)}

        finally:
            session.close()
    
    def get_blocked_members(self, clubId):
        session = self.Session()
        try:
            club = session.query(ClubModel).filter_by(id=clubId).first()
            if not club:
                return {"result": "error", "message": "noClubFound"}

            # Load blocked members from JSON
            blockedMembers = json.loads(club.blockedMembers)

            # Retrieve official names for the blocked members
            blockedMemberNames = [userId for userId in blockedMembers]

            return {"result": "success", "message": blockedMemberNames}

        except SQLAlchemyError as error:
            return {"result": "error", "message": str(error)}

        finally:
            session.close()

    def get_clubs(self):
        session = self.Session()
        try:
            clubs = session.query(ClubModel).all()
            return {"result": "success", "message": [data_to_dict(club) for club in clubs]}

        except SQLAlchemyError as error:
            return {"result": "error", "message": str(error)}

        finally:
            session.close()

    def update_club(self, club_info=None):
        session = self.Session()
        try:
            if not club_info:
                return {"result": "success", "message": "NoDataSupplied"}

            club = session.query(ClubModel).filter_by(id=club_info['id']).first()
            if not club:
                return {"result": "error", "message": {}}

            club.name = club_info.get("clubName", club.name)
            club.type = club_info.get("type", club.type)
            club.facultyAdvisor = club_info.get("facultyAdvisor", club.facultyAdvisor)
            club.studentLeaders = json.dumps(club_info.get("studentLeaders", club.studentLeaders))
            session.commit()
            return {"result": "success", "message": data_to_dict(club)}

        except SQLAlchemyError as error:
            session.rollback()
            return {"result": "error", "message": str(error)}

        finally:
            session.close()

    def update_description(self, name, description):
        session = self.Session()
        try:
            club = session.query(ClubModel).filter_by(name=name).first()
            if not club:
                return {"result": "error", "message": {}}

            club.description = description
            session.commit()
            return {"result": "success", "message": "clubDescriptionSuccessfullyUpdated"}

        except SQLAlchemyError as error:
            session.rollback()
            return {"result": "error", "message": str(error)}

        finally:
            session.close()

    def update_photo(self, name, photo):
        session = self.Session()
        try:
            club = session.query(ClubModel).filter_by(name=name).first()
            if not club:
                return {"result": "error", "message": {}}

            club.image = photo
            session.commit()
            return {"result": "success", "message": "clubPhotoSuccessfullyUpdated"}

        except SQLAlchemyError as error:
            session.rollback()
            return {"result": "error", "message": str(error)}

        finally:
            session.close()

    def blockMember(self, clubId=None, userId=None):
        session = self.Session()
        try:
            if clubId is None or userId is None:
                return {"result": "error", "message": "noDataSupplied"}

            club = session.query(ClubModel).filter_by(id=clubId).first()
            if club:
                blockedMembers = json.loads(club.blockedMembers)
                if userId in blockedMembers:
                    return {"result": "success", "message": "memberAlreadyBlocked"}
                else:
                    blockedMembers.append(userId)
                    club.blockedMembers=json.dumps(blockedMembers)
                    session.commit()
                    return {"result": "success", "message": "memberBlocked"}
            return {"result": "error", "message": "noClubFound"}
        except SQLAlchemyError as error:
            session.rollback()
            return {"result": "error", "message": str(error)}
        finally:
            session.close()
    
    def unBlockMember(self, clubId=None, userId=None):
        session = self.Session()
        try:
            if clubId is None or userId is None:
                return {"result": "error", "message": "noDataSupplied"}

            club = session.query(ClubModel).filter_by(id=clubId).first()
            if club:
                blockedMembers = json.loads(club.blockedMembers)
                if userId in blockedMembers:
                    return {"result": "success", "message": "memberAlreadyBlocked"}
                else:
                    blockedMembers.remove(userId)
                    club.blockedMembers=json.dumps(blockedMembers)
                    session.commit()
                    return {"result": "success", "message": "memberBlocked"}
            return {"result": "error", "message": "noClubFound"}
        except SQLAlchemyError as error:
            session.rollback()
            return {"result": "error", "message": str(error)}
        finally:
            session.close()

    def remove_club(self, name=None):
        session = self.Session()
        try:
            if not name:
                return {"result": "success", "message": "NoDataSupplied"}

            club = session.query(ClubModel).filter_by(name=name).first()
            if not club:
                return {"result": "error", "message": {}}

            session.delete(club)
            session.commit()
            return {"result": "success", "message": data_to_dict(club)}

        except SQLAlchemyError as error:
            session.rollback()
            return {"result": "error", "message": str(error)}

        finally:
            session.close()
    
    def get_clubId_from_name(self, name):
        session = self.Session()
        try:
            club = session.query(ClubModel).filter_by(name=name).first()
            if club:
                club = data_to_dict(club)
                return {"result": "success", "message": club["id"]}
            else:
                return None  # or raise an exception if desired
        except SQLAlchemyError as error:
            session.rollback()
            return {"result": "error", "message": str(error)}

        finally:
            session.close()
    
    def get_name_from_clubId(self, id):
        session = self.Session()
        try:
            club = session.query(ClubModel).filter(ClubModel.id == id).first()
            if club:
                club = data_to_dict(club)
                return {"result": "success", "message": club["name"]}
            else:
                return None  # or raise an exception if desired
        except SQLAlchemyError as error:
            session.rollback()
            return {"result": "error", "message": str(error)}

        finally:
            session.close()

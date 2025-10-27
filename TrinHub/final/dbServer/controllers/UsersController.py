from flask import request
from flask import jsonify
from models import UsersModel
from datetime import datetime
import re
import os


UsersModelTable = UsersModel.User(f"{os.getcwd()}/database/TrinHubDB.db")

# /users
def getUsers():
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="GET":
        users = UsersModelTable.get_users()["message"]
        return jsonify(users)
    else:
        return {}
    
def handleLogin():
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="POST":
        data = request.json
        email = data["email"]

        if not email.endswith("@trinityschoolnyc.org"):
            return "unauthorized domain", 401
        
        exists = UsersModelTable.exists(email=email)["message"]

        if exists:
            return '', 200
        else:
            preProcessedName = email.removesuffix("@trinityschoolnyc.org")
            preferredNameProcessedName = ''.join([character for character in preProcessedName if not character.isdigit()])
            prefferedName = preferredNameProcessedName.replace(".", " ").title()
            data["preferredName"] = prefferedName
            data["officialName"] = prefferedName

            createUser = UsersModelTable.create_user(data)

            return jsonify(createUser["message"])
    else:
        return {}

# /users/faculty
def getFaculty():
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="GET":
        users = UsersModelTable.get_users()["message"]
        faculty = []
        for user in users:
            email = user["email"]
            if not any(character.isdigit() for character in email):
                name = user["officialName"]
                id = user["id"]

                faculty.append({"name": name, "id": id})

        return jsonify(faculty)

    else:
        return {}

def getCurrentStudents():
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="GET":
        users = UsersModelTable.get_users()["message"]
        students = []
        currentDate = datetime.today().strftime('%Y %m').split(" ")
        currentDate = str(int(currentDate[0])+int(currentDate[1])/12)
        currentDate = float(str(currentDate)[2:])
        for user in users:
            email = user["email"]
            graduationYear = re.findall(r'\d+', email)
            if graduationYear != []:
                graduationYear = int(graduationYear[0])
                if (graduationYear-3.5<=currentDate<=graduationYear+0.5):
                    name = user["officialName"]
                    id = user["id"]

                    students.append({"name": name, "id": id})
        return jsonify(students)

    else:
        return {}

def getUser_updateUser_deleteUser():
    if request.method=="OPTIONS":
        return '', 200
    elif request.method=="GET":
        officialName = request.officialName
        user = UsersModelTable.get_user(officialName=officialName)["message"]
        return jsonify(user)
    elif request.method=="DELETE":
        officialName = request.officialName
        deletedUser = UsersModelTable.remove_user(officialName=officialName)["message"]

        return jsonify(deletedUser)
    else:
        return {}

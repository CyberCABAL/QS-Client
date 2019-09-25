from simple_rest_client.api import API
from simple_rest_client.resource import Resource
import time
import json
from pathlib import Path

"""Communication layer."""

class UserResource(Resource):
    actions = {
        "studentSubjects": {"method": "POST", "url": "res/studentSubjects"},
        "login": {"method": "POST", "url": "loginForm"},
        "logout": {"method": "GET", "url": "logout"},
        "addToQueue": {"method": "POST", "url": "res/addQueueElement"},
        "room": {"method": "GET", "url": "res/room"},
        "regSubjectSpecific": {"method": "POST", "url": "res/regSubjectSpecific"},
        "regSubjectGetTeachers": {"method": "POST", "url": "res/regSubjectGetTeachers"},
        "studentsInSubject": {"method": "POST", "url": "res/studentsInSubject"},
        "getStudentsInQueueElement": {"method": "POST", "url": "res/getStudentsInQueueElement"},
        "addPersonToQueueElement": {"method": "POST", "url": "res/addPersonToQueueElement"},
        "getQueueElement": {"method": "POST", "url": "res/getQueueElement"},
        "updateQueueElement": {"method": "POST", "url": "res/updateQueueElement"},
        "studentsInSubjectFromQueue": {"method": "POST", "url": "res/studentsInSubjectFromQueue"},
        "deleteQueueElement": {"method": "POST", "url": "res/deleteQueueElement"},
        "studentPostponeQueueElement": {"method": "POST", "url": "res/studentPostponeQueueElement"},
        "getQueue": {"method": "POST", "url": "res/getQueue"},
        "stopQueue": {"method": "POST", "url": "res/stopQueue"},
        "startQueue": {"method": "POST", "url": "res/startQueue"},
        "getQueueComment": {"method": "POST", "url": "res/getQueueComment"},
        "updateQueueComment": {"method": "POST", "url": "res/updateQueueComment"}
    };

header = {
    "Content-Type": "application/json;charset=utf-8",
    "Accept": "application/json, text/plain, */*",
    "Host": "qs.stud.iie.ntnu.no",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0",
    "Referer": "https://qs.stud.iie.ntnu.no",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive"
};

class QSPower:
    """Operations towards Qs."""
    def __init__(self):
        self.qs_api = API(
            api_root_url = "https://qs.stud.iie.ntnu.no/",
            headers = header,
            json_encode_body = True
        );
        self.qs_api.add_resource(resource_name = "qs", resource_class = UserResource);

    def printSubjects(self):
        for element in self.qs_api.qs.studentSubjects().body:
            print("Id:", element["subjectID"], element["subjectCode"], element["subjectName"]);

    def printRooms(self):
        for element in self.qs_api.qs.room().body:
            print("Id:", element["roomID"], element["roomNumber"]);

    def printQueue(self, subject_id):
        for element in self.qs_api.qs.getQueue(body = {"subjectID": subject_id}).body:
            #print(element);
            print(
                "Name:", element["personFirstName"], element["personLastName"],
                "Members:", element["groupmembers"],
                "queueEID:", element["queueElementID"],
                "subjectPID:", element["subjectPersonID"],
                "Room:", element["roomID"], element["roomNumber"],
                "Desk:", element["queueElementDesk"],
                "Msg:", element["queueElementMessage"],
                "Pos:", element["queueElementPosition"],
                "Help:", element["queueElementHelp"],
                "Teacher:", element["queueElementTeacher"],
                "Time:", element["queueElementStartTime"],
                "Exercises:", element["queueElementExercises"], "\n"
                );

    def printTeachers(self, subjectID):
        for element in self.qs_api.qs.regSubjectGetTeachers(body={"subjectID": subjectID}).body:
            print(element);

    def printStudents(self, subjectID):
        for element in self.qs_api.qs.studentsInSubject(body={"subjectID": subjectID}).body:
            print(element);

    def detectQueues(self):
        for x in range(0, 105):
            body = self.qs_api.qs.regSubjectSpecific(body={"subjectID": x}).body;
            if (len(body) != 0):
                if (body[0]["subjectQueueStatus"] == 1):
                    print(body);
                    print("\n");

    def login(self, user, passw):
        header["Cookie"] = self.qs_api.qs.login(body={"email": user,"password":passw}).headers["Set-Cookie"];

    def logout(self):
        self.qs_api.qs.logout();

    def waitQueue(self, subject_id, delay):
        subjectQueueStatus = 0;
        print("Waiting for queue " + str(subject_id));
        while (subjectQueueStatus != 1):
            try:
                subjectQueueStatus = self.qs_api.qs.regSubjectSpecific(body={"subjectID": subject_id}).body[0]["subjectQueueStatus"];
                if (subjectQueueStatus != 1):
                    time.sleep(delay); # Should use sockets.
            except :
                print("Timeout");
                time.sleep(delay * 2);
        print("Queue active");

    def addToQueue(self, subject_id, room_id, desk_id, message, h, tasks):
        return self.qs_api.qs.addToQueue(
        body = {
            "subjectID": subject_id,
            "roomID": room_id,
            "desk": desk_id,
            "message": message,
            "help": h,
            "exercises": tasks
            }
        ).body["queueElementID"];

    def joinQueueElement(self, queueElement_id, subjectPerson_id, tasks):
        return self.qs_api.qs.addPersonToQueueElement(
        body = {
            "queueElementID": queueElement_id,
            "subjectPersonID": subjectPerson_id,
            "exercises": tasks
            }
        );

    def delay(self, pos_id, nextPos_id, queueElement_id, subject_id):
        return self.qs_api.qs.studentPostponeQueueElement(
            body = {
                "queueElementPosition": pos_id,
                "queueElementPositionNext": nextPos_id,
                "queueElementID": queueElement_id,
                "subjectID": subject_id
                }
            );

    def upd(self, queueElementID):
        return self.qs_api.qs.updateQueueElement(body = {"roomID":1,"desk":1,"message":None,"help":1,"queueElementID":queueElementID});

    def update(self, roomID, desk, message, helpB, queueElementID):
        return self.qs_api.qs.updateQueueElement(
            body = {
                "roomID": roomID,
                "desk": desk,
                "message": message,
                "help": helpB,
                "queueElementID": queueElementID
                }
            );

    def start(self, subject_id):
        return self.qs_api.qs.startQueue(body = {"subjectID": subject_id});

    def end(self, subject_id):
        return self.qs_api.qs.stopQueue(body = {"subjectID": subject_id});

    def getComment(self, subject_id):
        return self.qs_api.qs.getQueueComment(body = {"subjectID": subject_id});

    def comment(self, subject_id, comment):
        return self.qs_api.qs.updateQueueComment(body = {"subjectQueueNotice": comment, "subjectID": subject_id});


from simple_rest_client.api import API
from simple_rest_client.resource import Resource
import time
import json
import getpass
from pathlib import Path
from qsLink import QSPower

"""Interface layer."""

# Observation of socket communication, which might be useful later;
# Socket: 42["80queueSocketEv", {time: "2018-03-06T15:21:44.627Z"}]		# three times
# Socket: 42["queueStartStopEv", {time: "2018-03-06T15:21:49.543Z"}]
# Request URL:wss://qs.stud.iie.ntnu.no/socket.io/?EIO=3&transport=websocket&sid=Jd_Q3ojLb2IHbX7bAA7c
# Request Method:GET
# Status Code:101 Switching Protocols

unlimitedPower = QSPower();

repeat = True;
myPos = None;
login = False;

def win():
    file = input("Enter file name to load queue data from('-1' to skip): ") + ".data";
    print();
    if (file != "-1.data"):
        if (Path(file).is_file()):
            with open(file) as data_file:
                data_loaded = json.load(data_file);
                subject_id = data_loaded["subject"];
                room_id = data_loaded["room"];
                desk_id = data_loaded["desk"];
            print("Queue data loaded from " + file);
    else:
        unlimitedPower.printSubjects();
        subject_id = int(input("Enter subject ID: "));
        print();

        unlimitedPower.printRooms();
        room_id = int(input("Enter room ID: "));
        desk_id = int(input("Enter desk ID: "));
        print();

        if (input("Do you want to save the data? (y/n) ") == "y"):
            writeFile(input("File name(without extension): ") + ".data", {"subject": subject_id,"room":room_id ,"desk":desk_id});

    h = needHelp();
    print();
    tasks = taskArray();
    print();

    unlimitedPower.waitQueue(subject_id, 3); # Max delay is 3 seconds. Faster than any human using a browser.
    #"Knowledge is power"
    queue_id = unlimitedPower.addToQueue(subject_id, room_id, desk_id, "Knowledge is power", h, tasks);
    print("Added to queue. Element ID is: ", queue_id);
    global myPos;
    myPos = queue_id;

def scan():
    unlimitedPower.detectQueues();

def subjects():
    unlimitedPower.printSubjects();

def checkID(params, inputText):
    ID = None;
    if (len(params) > 0):
        ID = params[0];
    while (not (ID or isinstance(ID, int))):
        ID = input(inputText);
    return ID;

"""def checkNParams(params, inputText, l):
    out = [];
    for i in range(l):
        if (len(params) > i):
            param = params[i];
        elif (not param):
            param = input(inputText[i]);
        out.append(param);
    return out;"""

def upd(params = []):
    unlimitedPower.upd(checkID(params, "ID: "));

def line(params = []):
    unlimitedPower.printQueue(checkID(params, "Subject ID: "));

def destroy(params = []):
    unlimitedPower.end(checkID(params, "ID: "));

def initiate(params = []):
    unlimitedPower.start(checkID(params, "ID: "));

def follow(params = []):
    if (len(params) > 0):
        element = params[0];
    if (element == "me" and myPos):
        element = myPos;
    elif (not element):
        element = input("Element ID: ");
    if (len(params) > 1):
        person = params[1];
    elif (not person):
        person = input("Subject PID: ");
    unlimitedPower.joinQueueElement(element, person, taskArray());
    print("Added", person, "to", element);

def leave():
    global login;
    if (login):
        unlimitedPower.logout();
        login = False;

def terminate():
    leave();
    global repeat;
    repeat = False;

def move(params):
    if (len(params) < 4):
        print("Insufficient parameteres for command");
        params = [input("Current: "), input("Target: "), input("queueEID: "), input("subjectID: ")];
    unlimitedPower.delay(params[0], params[1], params[2], params[3]);

def update(params):
    if (len(params) < 5):
        print("Insufficient parameteres for command");
        params = [input("Room: "), input("Desk: "), input("Message: "), needHelp(), input("queueEID: ")];
    unlimitedPower.update(params[0], params[1], params[2], params[3], params[4]);

def locateSuperiors(params = []):
    unlimitedPower.printTeachers(checkID(params, "Subject ID: "));

def enter(params = []):
    if (len(params) < 1):
        load = input("Load login?(y/n): ");
    load = params[0];
    global login;
    fileName = "qs.psw";
    if (load == "y"):
        if (Path(fileName).is_file()):
            with open(fileName) as data_file:
                data_loaded = json.load(data_file);
                username = data_loaded["email"];
                passw = data_loaded["password"];
            unlimitedPower.login(username, passw);
            passw = None;
            print("Login loaded from", fileName);
        else:
            print("Unable to locate file.")
            return False;
        login = True;
        return True;
    else:
        username = input("User: ");
        passw = getpass.getpass("Password: ");
        unlimitedPower.login(username, passw);
        if (input("Do you want to save the password (In plain text)? (y/n) ") == "y"):
            writeFile(fileName, {"email": username, "password": passw});
        login = True;
        return True;

def locateStudents(params = []):
    unlimitedPower.printStudents(checkID(params, "Subject ID: "));


def directives(x):
    """Command names."""
    return {
        "Win": win, # Wait for the queue.
        "Scan": scan,
        "Terminate": terminate,
        "Leaders": locateSuperiors,
        "Subjects": subjects,
        "Line": line, # Get queue.
        "Enter": enter,
        "Students": locateStudents,
        "Follow": follow, # Make someone join queue element.
        "Update": update,
        "Upd": upd,
        "Patience": move, # Change queue position.
        "Initiate": initiate, # Start queue.
        "Destroy": destroy, # Stop queue.
        "Leave": leave
        }.get(x, scan);

def taskArray():
    tasks = [];
    i = 0;
    print("Enter the tasks (-1 to stop)");
    while i != -1:
        i = int(input("Task: "));
        if (i != -1):
            tasks.append(i);
    return tasks;

def needHelp():
    return False if (input("Help?(n for approve, y for help): ") == "n") else True

def writeFile(file, data):
    with open(file, "w") as outfile:
        json.dump(data, outfile);
    print("Data saved in " + file);

while(repeat):
    print("\nDirective: ");
    d = input().split(" ");
    directive = d[0];
    params = d[1:];
    if (directive):
        if(len(params) >= 1):
            directives(directive)(params);
        else:
            directives(directive)();

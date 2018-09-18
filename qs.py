from simple_rest_client.api import API
from simple_rest_client.resource import Resource
import time
import json
from pathlib import Path

class UserResource(Resource):
    actions = {
        'studentSubjects': {'method': 'POST', 'url': 'studentSubjects'},
        'login': {'method': 'POST', 'url': 'https://qs.stud.iie.ntnu.no/loginForm'},
        'addToQueue': {'method': 'POST', 'url': 'addQueueElement'},
		'postpone': {'method': 'POST', 'url': 'studentPostponeQueueElement'},
		'getQueue': {'method': 'POST', 'url': 'getQueue'},
        'room': {'method': 'GET', 'url': 'room'}
    }

header = {
    'Content-Type': 'application/json;charset=UTF-8',
    'Accept': 'application/json, text/plain, */*',
    'Host': 'qs.stud.iie.ntnu.no',
    'Origin': 'https://qs.stud.iie.ntnu.no',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'DNT': '1',
    'Referer': 'https://qs.stud.iie.ntnu.no/student',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'nb-NO,nb;q=0.8,no;q=0.6,nn;q=0.4,en-US;q=0.2,en;q=0.2,da;q=0.2'
    }
qs_api = API(
    api_root_url='https://qs.stud.iie.ntnu.no/res/', 
	headers=header,
    json_encode_body=True
)
qs_api.add_resource(resource_name='qs', resource_class=UserResource)

if Path("qs.psw").is_file() :
    with open('qs.psw') as data_file:
        data_loaded = json.load(data_file)
        username = data_loaded["email"]
        passwd = data_loaded["password"]
    print("Username and password loaded from qs.psw")
else:
    username =  input("Username: ")
    passwd = input("Password: ")
    if input("Do you want to save the password? (y/n)") == "y":
        with open('qs.psw', 'w') as outfile:
            json.dump({"email": username,"password":passwd}, outfile)
    print("Username and passwd saved to qs.psw")

req = qs_api.qs.login(body={"email": username,"password":passwd})
header['Cookie'] = req.headers["Set-Cookie"]

for element in qs_api.qs.studentSubjects().body:
    if element['subjectActive'] != 0:
        print("Id:",element['subjectID'], element['subjectCode'], element['subjectName'])

subject_id = int(input('Enter subject ID: '))

rooms = qs_api.qs.room().body

for element in rooms:
    print("Id:",element['roomID'], element['roomNumber'])

room_id = int(input('Enter room ID: '))
desk_id = int(input('Enter desk ID: '))

tasks = []
i = -1

print("Add tasks (0 to exit)")
while i != 0 or tasks.__len__() == 0:
    i = int(input("Add task: "))
    if i !=0:
        tasks.append(i)
        print("Tasks: ", tasks)

subjectQueueStatus = 0

help = False
if input("Help? (y/n)") == "y":
	help = True

print("Wainting for queue")

while (subjectQueueStatus == 0):    
    for element in qs_api.qs.studentSubjects().body:
        if (element['subjectID'] == subject_id):
            subjectQueueStatus = element['subjectQueueStatus']
    time.sleep(3)
    
print("Queue open")
queue_id = qs_api.qs.addToQueue(body={"subjectID": subject_id,"roomID": room_id,"desk": desk_id,"message":"","help":help,"exercises":tasks}).body["queueElementID"]

print("Added to queue")

def goUp():
	usedPos = []

	for element in qs_api.qs.getQueue(body={"subjectID": subject_id}).body:
		print(element)
		
		usedPos.append(element["queueElementPosition"])
		
		#for i in range(element["queueElementPosition"]):
			#qs_api.qs.postpone(body={"queueElementPosition":element["queueElementPosition"],"queueElementPositionNext":0,"queueElementID":queue_id,"subjectID":subject_id})
		if element["queueElementID"] == queue_id:
			queueMaxPos = element["queueElementPosition"]
			
			currentPos = element["queueElementPosition"]
		
			for i in range(element["queueElementPosition"] - 1):
				
				if (currentPos - i) in usedPos:
					time.sleep(1.5)
					print(queueMaxPos - i - 1)
					qs_api.qs.postpone(body={"queueElementPosition":currentPos,"queueElementPositionNext": queueMaxPos - i - 1,"queueElementID":queue_id,"subjectID":subject_id})
					currentPos = queueMaxPos - i - 1

def upAndDown():

	usedPos = []

	for element in qs_api.qs.getQueue(body={"subjectID": subject_id}).body:
		print(element)
		
		usedPos.append(element["queueElementPosition"])
		
		#for i in range(element["queueElementPosition"]):
			#qs_api.qs.postpone(body={"queueElementPosition":element["queueElementPosition"],"queueElementPositionNext":0,"queueElementID":queue_id,"subjectID":subject_id})
		if element["queueElementID"] == queue_id:
			queueMaxPos = element["queueElementPosition"]
			
			currentPos = element["queueElementPosition"]
		
			for i in range(element["queueElementPosition"] - 1):
				
				if (currentPos - i) in usedPos:
					time.sleep(1.5)
					print(queueMaxPos - i - 1)
					qs_api.qs.postpone(body={"queueElementPosition":currentPos,"queueElementPositionNext": queueMaxPos - i - 1,"queueElementID":queue_id,"subjectID":subject_id})
					currentPos = queueMaxPos - i - 1
			
			"""
			for element in qs_api.qs.getQueue(body={"subjectID": subject_id}).body:
				print(element)
				
				#for i in range(element["queueElementPosition"]):
					#qs_api.qs.postpone(body={"queueElementPosition":element["queueElementPosition"],"queueElementPositionNext":0,"queueElementID":queue_id,"subjectID":subject_id})
				if element["queueElementID"] == queue_id:
					
					for i in range(queueMaxPos):
						print(i);
						time.sleep(0.2)
						qs_api.qs.postpone(body={"queueElementPosition":element["queueElementPosition"] + i,"queueElementPositionNext": element["queueElementPosition"] + i + 1,"queueElementID":queue_id,"subjectID":subject_id})
						"""

						
if input("Go to top? (y/n)") == "y":
	goUp()
	print("Moved to top.")

#queueElement 
#while ():

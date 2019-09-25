from simple_rest_client.api import API
from simple_rest_client.resource import Resource
import time
import json
from pathlib import Path

class UserResource(Resource):
    actions = {
        "regSubjectSpecific": {"method": "POST", "url": "res/regSubjectSpecific"},
	"login": {"method": "POST", "url": "loginForm"}
    }

header = {
    "Content-Type": "application/json;charset=utf-8",
    "Accept": "application/json, text/plain, */*",
    "Host": "qs.stud.iie.ntnu.no",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0",
    "Referer": "https://qs.stud.iie.ntnu.no",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive"
    }

"""Example for finding all open queues."""

def result():
    for x in range(0, 125):
        body = qs_api.qs.regSubjectSpecific(body={"subjectID": x}).body
        if (len(body) != 0):
            if (body[0]["subjectQueueStatus"] == 1):
                print(body)
                print("\n")

def login(user, passw):
    header["Cookie"] = qs_api.qs.login(body={"email": user, "password":passw}).headers["Set-Cookie"]


qs_api = API(
    api_root_url = "https://qs.stud.iie.ntnu.no/",
    headers = header,
    json_encode_body = True,
    append_slash = False
)
qs_api.add_resource(resource_name = "qs", resource_class = UserResource)

loginSuccess = False
if (input("Load login?(y/n): ") == "y"):
    if (Path("qs.psw").is_file()):
        with open("qs.psw") as data_file:
            data_loaded = json.load(data_file)
            username = data_loaded["email"]
            passw = data_loaded["password"]
        login(username, passw)
        loginSuccess = True
        print("Login loaded from qs.psw")
else:
    username = input("Username: ")
    passw = input("Password: ")
    login(username, passw)
    loginSuccess = True
    if (input("Do you want to save the password? (y/n) ") == "y"):
        writeFile("qs.psw", {"email": username,"password":passw})

if (loginSuccess):
  result()
else:
    print("Login failed")

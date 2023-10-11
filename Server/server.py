import threading
import sys
import time
import json
from socket import *


def requestTCP(socket, address):
    sentence = socket.recv(1024)


def addUserOnline(user, ip, port):
    usersOnline[user] = {'status': 'inactive', 'ip': ip, 'port': port}


def changeStatusUserOnline(user):
    if usersOnline[user]['status'] == 'active':
        usersOnline[user]['status'] == 'inactive'
    else:
        usersOnline[user]['status'] == 'active'


def delUserOnline(user):
    usersOnline.pop(user)


def ReturnUsersOnline():
    stringAnswer = ''
    for user in usersOnline:
        stringAnswer = f"{stringAnswer}User: {user} / Status: {usersOnline[user]['status']} / Ip: {usersOnline[user]['ip']} / Port: {usersOnline[user]['port']}\n"
    return stringAnswer


def addUsersPlaying(firstUser, secondUser):
    usersPlaying[firstUser + 'X' + secondUser] = {'ip': [usersOnline[firstUser]['ip'], usersOnline[secondUser]['ip']], 'port': [
        usersOnline[firstUser]['port'], usersOnline[secondUser]['port']]}
    changeStatusUserOnline(firstUser)
    changeStatusUserOnline(secondUser)


def delUsersPlaying(firstUser, secondUser):
    usersOnline.pop(firstUser + 'X' + secondUser)
    changeStatusUserOnline(firstUser)
    changeStatusUserOnline(secondUser)


def loadData(file):
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return (data)


def saveData(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def verifyUserExistence(user):
    if user in usersData:
        return True
    return False


def registerUser(name, user, password):
    usersData[user] = {'name': name, 'password': password}
    saveData('../Data/loginData.json', usersData)


def deleteUser(user):
    usersData.pop(user)
    saveData('../Data/loginData.json', usersData)


serverPort = 12000
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(("", serverPort))
serverSocket.listen(1)

# usersOnline format:
# {
#   'user':{
#       'status': 'active' | 'inactive',
#       'ip': '',
#       'port':
#       },
#   'userN': {...}
# }
usersOnline = {}

# usersPlaying format:
# {
#   '<first_user>X<second_user>':
#       {
#       ip: ['', ''],
#       port: ['', '']
#       },
#   '<first_user>X<second_user>':
#       {...}
# }
usersPlaying = {}

usersData = loadData('../Data/loginData.json')
# {
#   'user':{
#       'name': '',
#       'password': '',
#       },
#   'userN': {...}
# }

# while 1:
#     threading.Thread(target=requestTCP, args=(serverSocket.accept()))

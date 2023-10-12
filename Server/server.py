import threading
import sys
import time
import json
from socket import *


def requestTCP(socket, address):
    sentence = socket.recv(1024)


def registerLog(users, type):
    localTime = time.localtime()
    localTime = f"{localTime.tm_hour}:{localTime.tm_min}:{localTime.tm_sec} {localTime.tm_mday}/{localTime.tm_mon}/{localTime.tm_year}"
    match(type):
        case 'register':
            appendData('../Data/game.log',
                       f"{localTime}: User {users[0]} registered\n")
        case 'conect':
            appendData('../Data/game.log',
                       f"{localTime}: User {users[0]} connected\n")
        case 'timeout':
            appendData('../Data/game.log',
                       f"{localTime}: User {users[0]} does not reply (timeout)\n")
        case 'inactive':
            appendData('../Data/game.log',
                       f"{localTime}: User {users[0]} became inactive\n")
        case 'active':
            appendData('../Data/game.log',
                       f"{localTime}: User {users[0]} became active\n")
        case 'playing':
            appendData('../Data/game.log',
                       f"{localTime}: Users {users[0]} and {users[1]} are playing\n")
        case 'disconnect':
            appendData('../Data/game.log',
                       f"{localTime}: User {users[0]} disconnected\n")


def addUserOnline(user, ip, port):
    usersOnline[user] = {'status': 'inactive', 'ip': ip, 'port': port}
    registerLog([user], 'connect')


def changeStatusUserOnline(user):
    if usersOnline[user]['status'] == 'active':
        usersOnline[user]['status'] == 'inactive'
        registerLog([user], 'inactive')
    else:
        usersOnline[user]['status'] == 'active'
        registerLog([user], 'active')


def delUserOnline(user):
    usersOnline.pop(user)
    registerLog([user], 'disconnect')


def returnUserData(user):
    return f"User: {user} / Status: {usersOnline[user]['status']} / Ip: {usersOnline[user]['ip']} / Port: {usersOnline[user]['port']}\n"


def returnUsersOnline():
    stringAnswer = ''
    for user in usersOnline:
        stringAnswer = f"{stringAnswer}{returnUserData(user)}"
    return stringAnswer


def addUsersPlaying(firstUser, secondUser):
    usersPlaying[firstUser + 'X' + secondUser] = {'ip': [usersOnline[firstUser]['ip'], usersOnline[secondUser]['ip']], 'port': [
        usersOnline[firstUser]['port'], usersOnline[secondUser]['port']]}
    registerLog([firstUser, secondUser], 'playing')
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


def appendData(file, data):
    with open(file, "a", encoding="utf-8") as f:
        f.write(data)


def verifyUserExistence(user):
    if user in usersData:
        return True
    return False


def registerUser(name, user, password):
    usersData[user] = {'name': name, 'password': password}
    registerLog([user], 'register')
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

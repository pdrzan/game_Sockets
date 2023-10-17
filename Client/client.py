import sys
import time
from socket import *
from threading import *

idMessage = 0
idSemaphone = Semaphore(1)
sock = socket(AF_INET, SOCK_DGRAM)
sock.settimeout(5)
playingWith = '' # opponent user
recieveMessages = {}
connected = False
semaphore = Semaphore(1)  


def startRecivingMessages():
    while connected:
        msg = sock.recvfrom(1024)
        id = msg.split()[0]
        recieveMessages[id] = msg[len(id):]

def addIdMessage(message):
    idSemaphone.acquire()
    message = f'{idMessage} {message}'
    idMessage += 1
    idSemaphone.release()
    return message, idMessage


def sendMessage(message, address=('', 12000)):
    message = addIdMessage(message)
    sock.sendto(bytes(message, "utf-8"), address)


def sendReceiveMessage(message, address=('', 12000)):
    sendMessage(message, address)
    return sock.recv(1024)


def printSeparator(message=''):
    if message != '':
        print(message)
    print("=" * 50)


def getLoginInformation():
    name = input("Name: ")
    user = input("User: ")
    password = input("Password: ")
    return name, user, password


def login():
    receivedMessage = ''
    printSeparator("Login in:")
    name, user, password = getLoginInformation()
    while receivedMessage != "Successfully authenticated":
        printSeparator("Wrong credentails. Try again:")
        name, user, password = getLoginInformation()
        receivedMessage = sendReceiveMessage(f"login {name} {user} {password}")
    return user


def listUserOnline(user):
    receivedMessage = sendReceiveMessage(f'listOnline {user}')
    print(receivedMessage)


def listUserPlaying(user):
    receivedMessage = sendReceiveMessage(f'listPlaying {user}')
    print(receivedMessage)


def inviteToPlay(user, opponent):
    sendMessage(
        f'opponentInformation {user} {opponent}')
    if receivedMessage != "Opponent not found":
        receivedMessage = receivedMessage.split()
        address = (receivedMessage[0], int(receivedMessage[1]))
        receivedMessage = sendReceiveMessage('GAME_INI', address)
        if (receivedMessage == 'GAME_ACK'):
            sendMessage(f'playing {user} {opponent}')
            return True, address
    return False, address


def play(user, opponent):
    semaphore.release()
    playingWith = opponent
    playing, addressOponent = inviteToPlay(user, opponent)
    while playing and playingWith == opponent:
        
    if playing:
        semaphore.acquire()
        print(f"Another match was accepted. The match with {opponent} is over.")
        semaphore.release()
    else:
        semaphore.acquire()
        print(f"The user {opponent} didn't accepted your invite")
        semaphore.release()
    return

def printOptions():
    print("Choose a option:")
    print("1. LIST-USER-ON-LINE")
    print("2. LIST-USER-PLAYING")
    print("3. PLAY")
    print("9. DISCONNECT")


def getOption():
    printOptions()
    return int(input())

def main():
    playing = False
    user = login()
    connected = True
    while connected:
        semaphore.acquire()
        option = getOption()
        match(option):
            case 1:
                listUserOnline(user)
                semaphore.release()
            case 2:
                listUserPlaying(user)
                semaphore.release()
            case 3:
                opponent = input("Type the user you wanna play with:")
                play(user, opponent)
            case 9:
                connected = False
    return

import sys
import time
from socket import *
import threading
from threading import *


def startRecivingMessages():
    while connected:
        try:
            message, address = sock.recvfrom(1024)
            message = message.decode('utf-8')
            print(message)
            localIdMessage = message.split()[0]
            if (message.split()[1] == 'GAME_INI'):
                print("Entrou")
                (threading.Thread(target=invitedToPlay, args=(message, address))).start()
            elif (message.split()[1] == 'GAME_OVER'):
                (threading.Thread(target=recivedGameOver, args=(message))).start()
            else:
                recievedMessages[localIdMessage] = message[len(
                    localIdMessage) + 1:]
        except:
            if not connected:
                break


def addIdMessage(message):
    global idMessage
    idSemaphone.acquire()
    message = f'{idMessage} {message}'
    idMessage += 1
    idSemaphone.release()
    return message


def addGameIdMessage(message):
    return f'GAME {message}'


def getIdMessage(message):
    return message.split()[0]


def sendMessage(message, address=('', 12000), addId=True):
    if addId:
        message = addIdMessage(message)
        localIdMessage = getIdMessage(message)
    else:
        message = str(message)
    sock.sendto(bytes(message, "utf-8"), address)
    if addId:
        return localIdMessage


def sendReceiveMessage(message, address=('', 12000)):
    localIdMessage = sendMessage(message, address)
    timeout = 5
    while localIdMessage not in recievedMessages and timeout > 0:
        time.sleep(0.3)
        timeout -= 0.3
    if timeout > 0:
        return recievedMessages.pop(localIdMessage)
    return 'Message Error'


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
    printSeparator("Login in:")
    name, user, password = getLoginInformation()
    receivedMessage = sendReceiveMessage(f"login {name} {user} {password}")
    while receivedMessage != "Successfully authenticated":
        semaphore.acquire()
        printSeparator("Wrong credentails. Try again:")
        name, user, password = getLoginInformation()
        semaphore.release()
        receivedMessage = sendReceiveMessage(f"login {name} {user} {password}")
    return user


def listUserOnline(user):
    receivedMessage = sendReceiveMessage(f'listOnline {user}')
    print(receivedMessage)


def listUserPlaying(user):
    receivedMessage = sendReceiveMessage(f'listPlaying {user}')
    print(receivedMessage)


def getUserInformation(user, opponent):
    return sendReceiveMessage(
        f'userInformation {user} {opponent}')

def inviteToPlay(user, opponent):
    receivedMessage = getUserInformation(user, opponent)
    print(receivedMessage)
    if receivedMessage != "Opponent not found" and receivedMessage != 'Message Error':
        receivedMessage = receivedMessage.split()
        address = (receivedMessage[0], int(receivedMessage[1]))
        print(address)
        receivedMessage = sendReceiveMessage(f'GAME_INI {user}', address)
        print("Receive: ", receivedMessage)
        if (receivedMessage == 'GAME_ACK'):
            sendMessage(f'playing {user} {opponent}')
            return True, address
    return False, address


def stopPlaying(address):
    global playingWith, playing
    if playingWith != '':
        playingWith = ''
        sendGameOver(address)
    playing = False


def invitedToPlay(message, address):
    global playing
    playing = True
    semaphore.acquire()
    opponent = message.split()[2]
    print(f"The user {opponent} invited you to play")
    answer = input("Type y to accept and any other key to decline")
    semaphore.release()
    if answer == 'y':
        localIdMessage = message.split()[0]
        sendMessage(f"{localIdMessage} GAME_ACK", address, False)
        stopPlaying(address)
        play(opponent, address)


def printGameOver():
    print("The game with {opponent} is over")


def recivedGameOver(message):
    semaphore.acquire()
    stopPlaying()
    printGameOver()
    semaphore.release()


def sendGameOver(address):
    semaphore.acquire()
    sendMessage("GAME_OVER", address)
    printGameOver()
    semaphore.release()


def play(opponent, addressOponent):
    global playing, playingWith
    playingWith = opponent
    playing = True
    # while playing and playingWith == opponent:
    #     # TO DO implement the game
    #     opponent = opponent
    semaphore.acquire()
    if playing:
        print(
            f"Another match was accepted. The match with {opponent} is over.")
    else:
        print(f"The user {opponent} didn't accepted your invite")
    stopPlaying(addressOponent)
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


idMessage = 0
idSemaphone = Semaphore(1)
serverPort = int(input("Plese, type a number port greater than 1024: "))
sock = socket(AF_INET, SOCK_DGRAM)
sock.bind(("", serverPort))
sock.settimeout(5)
playingWith = ''  # opponent user
recievedMessages = {}
connected = True
semaphore = Semaphore(1)


def main():
    global connected, playing, serverPort
    (threading.Thread(target=startRecivingMessages, args=())).start()
    playing = False
    user = login()
    connected = True
    while connected:
        if not playing:
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
                    semaphore.release()
                    playing, addressOponent = inviteToPlay(user, opponent)
                    if playing:
                        play(opponent, addressOponent)
                case 9:
                    connected = False
    sock.close()
    return


if __name__ == "__main__":
    main()

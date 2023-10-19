import sys
import time
from socket import *
import threading
from threading import *


def startRecivingMessages():
    while connected:
        try:
            message, address = sock.recvfrom(1024)
            message = decodeByteToString(message)
            localIdMessage = getFirstWord(message)
            if (message.split()[1] == 'GAME_INI'):
                (threading.Thread(target=invitedToPlay, args=(message, address))).start()
            elif (message.split()[1] == 'GAME_OVER'):
                (threading.Thread(target=recivedGameOver, args=(address))).start()
            else:
                recievedMessages[localIdMessage] = message[len(
                    localIdMessage) + 1:]
        except:
            if not connected:
                break


def decodeByteToString(message):
    return message.decode('utf-8')


def toBytes(message):
    return bytes(message, "utf-8")

def addIdMessage(message):
    global idMessage
    idSemaphone.acquire()
    message = f'{idMessage} {message}'
    idMessage += 1
    idSemaphone.release()
    return message


def addGameIdMessage(message):
    return f'GAME {message}'


def getFirstWord(message):
    return message.split()[0]


def sendMessage(message, address=('', 12000), addId=True):
    if addId:
        message = addIdMessage(message)
    sock.sendto(toBytes(message), address)
    return getFirstWord(message)


def sendReceiveMessage(message, address=('', 12000), addId=True, hasTimeOut=True):
    localIdMessage = sendMessage(message, address, addId)
    return recieveMessage(localIdMessage, hasTimeOut)


def recieveMessage(localIdMessage, hasTimeOut=True):
    timeout = 10
    while localIdMessage not in recievedMessages and timeout > 0:
        time.sleep(0.3)
        if hasTimeOut:
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
        semaphorePrint.acquire()
        printSeparator("Wrong credentails. Try again:")
        name, user, password = getLoginInformation()
        semaphorePrint.release()
        receivedMessage = sendReceiveMessage(f"login {name} {user} {password}")
    return user


def listUserOnline(user):
    print(sendReceiveMessage(f'listOnline {user}'))


def listUserPlaying(user):
    print(sendReceiveMessage(f'listPlaying {user}'))


def getUserInformation(user, opponent):
    return sendReceiveMessage(
        f'userInformation {user} {opponent}')


def inviteToPlay(user, opponent):
    global playing, clientInititedTheGame
    receivedMessage = getUserInformation(user, opponent)
    if receivedMessage != "Opponent not found" and receivedMessage != 'Message Error':
        ipOpponent, portOpponent = receivedMessage.split()
        address = (ipOpponent, int(portOpponent))
        receivedMessage = sendReceiveMessage(f'GAME_INI {user}', address)
        if (receivedMessage == 'GAME_ACK'):
            clientInititedTheGame = True
            playing = True
            sendMessage(f'playing {user} {opponent}')
    return address


def stopPlaying(opponent):
    global playing
    if playing:
        printGameOver(opponent)
    playing = False
    

def getResponseInvite(opponent):
    print(f"The user {opponent} invited you to play")
    return input("Type y to accept and any other key to decline: ")

def invitedToPlay(message, address):
    global playing, wasInvitedToPlay
    wasInvitedToPlay = True
    semaphorePrint.acquire()
    opponent = message.split()[2]
    answer = getResponseInvite(opponent)
    semaphorePrint.release()
    if answer == 'y':
        recivedIdMessage = getFirstWord(message)
        sendMessage(f"{recivedIdMessage} GAME_ACK", address, False)
        stopPlaying(opponent)
        (threading.Thread(target=play, args=(opponent, address))).start()
    wasInvitedToPlay = False


def printGameOver(opponent):
    print(f"The game with {opponent} is over")


def recivedGameOver(address):
    semaphorePrint.acquire()
    stopPlaying(address)
    printGameOver()
    semaphorePrint.release()


def sendGameOver(address):
    semaphorePrint.acquire()
    sendMessage("GAME_OVER", address)
    semaphorePrint.release()


def printGameOptions(clientInititedTheGame):
    print("Choose a option:")
    if not clientInititedTheGame:
        print("1. Guess a letter")
        print("2. Guess the word")
        print("3. Quit the game")
    else:
        print("1. Continue playing")
        print("2. Quit the game")


def getOptionGame(clientInititedTheGame):
    printGameOptions(clientInititedTheGame)
    return int(input("Option: "))

def processOptionGame(option, address):
    match(option):
        case 1:
            letter = input("Type the letter: ")
            sendMessage(f"GAME {letter}", address, False)
        case 2:
            word = input("Type the word: ")
            sendMessage(f"GAME {word}", address, False)
        case 3:
            stopPlaying(address)


def returnWordLettersFound(secretWord, letters):
    wordLetterFound = ''
    for letter in secretWord:
        if letter == ' ':
            wordLetterFound += ' '
        elif letter in letters:
            wordLetterFound += letter
        else:
            wordLetterFound += '_'
    return wordLetterFound


def returnLenWord(word):
    return len(word.replace(' ', ''))


def returnLettersMissing(word, letters):
    count = 0
    for letter in word:
        if letter not in letters:
            count += 1
    return count

def opponentWin(address, secretWord):
    global playing
    sendMessage(f"GAME WIN {secretWord}", address, False)
    print("You losed, maybe next time...")
    printSeparator()
    playing = False


def opponentLose(address, secretWord):
    global playing
    sendMessage(f"GAME LOSE {secretWord}", address, False)
    print("You won, Congrats!")
    printSeparator()
    playing = False


def excludeFirstWord(message):
    return message.replace(f"{message.split()[0]} ", '')

def processResult(message):
    global playing
    result = getFirstWord(message)
    message = excludeFirstWord(message)
    semaphorePrint.acquire()
    match(result):
        case "WIN":
            print("You won, Congrats!")
        case "LOSE":
            print("You losed, maybe next time...")
    print(f"The secret word was: {message}")
    semaphorePrint.release()
    playing = False

def pringHangManWord(word, tries):
    match(tries):
        case 0:
            print( "______    ")
            print( "|         ")
            print( "|         ")
            print(f"|         {word}")
        case 1:
            print( "______    ")
            print( "|    0    ")
            print( "|         ")
            print(f"|         {word}")
        case 2:
            print( "______    ")
            print( "|    0    ")
            print( "|    |    ")
            print(f"|         {word}")
        case 3:
            print( "______    ")
            print( "|    0    ")
            print( "|   -|    ")
            print(f"|         {word}")
        case 4:
            print( "______    ")
            print( "|    0    ")
            print( "|   -|-   ")
            print(f"|         {word}")
        case 5:
            print( "______    ")
            print( "|    0    ")
            print( "|   -|-   ")
            print(f"|   /     {word}")
        case 6:
            print( "______    ")
            print( "|    0    ")
            print( "|   -|-   ")
            print(f"|   / \   {word}")
    print("\n")


def play(opponent, addressOponent):
    global playing, wasInvitedToPlay
    playing = True
    if clientInititedTheGame:
        semaphorePrint.acquire()
        secretWord = input("Type the secret word: ")
        semaphorePrint.release()

        lettersMissing = returnLenWord(secretWord)
        letters = []
        tries = 0

        while playing:
            if not wasInvitedToPlay:
                option = getOptionGame(clientInititedTheGame)
                match(option):
                    case 1:
                        recievedMessage = sendReceiveMessage(
                            f"GAME {tries} {returnWordLettersFound(secretWord, letters)}", addressOponent, False, False)
                        if(len(recievedMessage) == 1):
                            if recievedMessage not in letters:
                                letters.append(recievedMessage)
                            if lettersMissing > returnLettersMissing(secretWord, letters):
                                lettersMissing = returnLettersMissing(secretWord, letters)
                                if(lettersMissing == 0):
                                    opponentWin(addressOponent, secretWord)
                            else:
                                tries += 1
                        else:
                            if recievedMessage == secretWord:
                                opponentWin(addressOponent, secretWord)
                            else:
                                tries += 1
                        if(tries >= 6):
                            opponentLose(addressOponent, secretWord)
                    case 2:
                        stopPlaying(addressOponent)
    else:   
        while playing:
            if not wasInvitedToPlay:
                recievedMessage = recieveMessage("GAME")
                if recievedMessage != "Message Error":
                    if(getFirstWord(recievedMessage) != "WIN" and getFirstWord(recievedMessage) != "LOSE"):
                        tries = int(getFirstWord(recievedMessage))
                        recievedMessage = excludeFirstWord(recievedMessage)
                        pringHangManWord(recievedMessage, tries)
                        semaphorePrint.acquire()
                        option = getOptionGame(clientInititedTheGame)
                        processOptionGame(option, addressOponent)
                        semaphorePrint.release()
                    else:
                        processResult(recievedMessage)
                        
    # semaphorePrint.acquire()
    # print(f"Another match was accepted. The match with {opponent} is over.")
    # semaphorePrint.release()
    return


def printOptions():
    print("Choose a option:")
    print("1. LIST-USER-ON-LINE")
    print("2. LIST-USER-PLAYING")
    print("3. PLAY")
    print("9. DISCONNECT")


def getOption():
    printOptions()
    return int(input("Option: "))


idMessage = 0
idSemaphone = Semaphore(1)
semaphorePrint = Semaphore(1)

serverPort = int(input("Plese, type a number port greater than 1024: "))
sock = socket(AF_INET, SOCK_DGRAM)
sock.bind(("", serverPort))
sock.settimeout(5)

wasInvitedToPlay = False
clientInititedTheGame = False
recievedMessages = {}
connected = True


def main():
    global connected, playing
    playing = False

    (threading.Thread(target=startRecivingMessages, args=())).start()

    user = login()
    while connected:
        if not wasInvitedToPlay and not playing:
            semaphorePrint.acquire()
            option = getOption()
            match(option):
                case 1:
                    listUserOnline(user)
                    semaphorePrint.release()
                case 2:
                    listUserPlaying(user)
                    semaphorePrint.release()
                case 3:
                    opponent = input("Type the user you wanna play with: ")
                    semaphorePrint.release()
                    addressOponent = inviteToPlay(user, opponent)
                    if playing:
                        play(opponent, addressOponent)
                case 9:
                    connected = False
            printSeparator()
    sock.close()
    return


if __name__ == "__main__":
    main()

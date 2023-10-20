import time
from socket import *
import threading
from threading import *


def startRecivingMessages():
    global recivedGameOver
    while connected:
        try:
            message, address = sock.recvfrom(1024)
            message = decodeByteToString(message)
            localIdMessage = getFirstWord(message)
            if (message.split()[1] == 'GAME_INI'):
                (threading.Thread(target=invitedToPlay, args=(message, address))).start()
            elif (message.split()[1] == 'GAME_OVER'):
                recivedGameOver = True
                (threading.Thread(target=stopPlaying, args=())).start()
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
    semaphorePrint.acquire()
    name, user, password = getLoginInformation()
    semaphorePrint.release()
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
        receivedMessage = sendReceiveMessage(
            f'GAME_INI {user}', address, True, False)
        if (receivedMessage == 'GAME_ACK'):
            clientInititedTheGame = True
            sendMessage(f'playing {user} {opponent}')
            return address
    return ''


def stopPlaying():
    global playing
    playing = False


def getResponseInvite(opponent):
    print(f"The user {opponent} invited you to play")
    return input("Type y to accept and any other key to decline: ")


def invitedToPlay(message, address):
    global wasInvitedToPlay
    wasInvitedToPlay = True
    semaphorePrint.acquire()
    opponent = message.split()[2]
    answer = getResponseInvite(opponent)
    semaphorePrint.release()
    if answer == 'y':
        recivedIdMessage = getFirstWord(message)
        sendMessage(f"{recivedIdMessage} GAME_ACK", address, False)
        stopPlaying()
        (threading.Thread(target=play, args=(opponent, address))).start()
    wasInvitedToPlay = False


def printGameOver(opponent):
    semaphorePrint.acquire()
    print(f"The game with {opponent} is over")
    semaphorePrint.release()


def sendGameOver(address):
    sendMessage("GAME_OVER", address)


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
    try:
        return int(input("Option: "))
    except:
        printInvalid()
        return getOptionGame(clientInititedTheGame)


def processOptionGame(option, addressOpponent):
    match(option):
        case 1:
            letter = input("Type the letter: ")
            sendMessage(f"GAME {letter}", addressOpponent, False)
        case 2:
            word = input("Type the word: ")
            sendMessage(f"GAME {word}", addressOpponent, False)
        case 3:
            stopPlaying()


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
        if letter != ' ' and letter not in letters:
            count += 1
    return count

def printWin():
    print("You won, Congrats!")
    printSeparator()


def printLose():
    print("You losed, maybe next time...")
    printSeparator()

def opponentWin(address, secretWord):
    global playing
    sendMessage(f"GAME WIN {secretWord}", address, False)
    printLose()
    stopPlaying()


def opponentLose(address, secretWord):
    global playing
    sendMessage(f"GAME LOSE {secretWord}", address, False)
    printWin()
    stopPlaying()


def excludeFirstWord(message):
    return message.replace(f"{message.split()[0]} ", '')


def processResult(message):
    global playing
    result = getFirstWord(message)
    message = excludeFirstWord(message)
    semaphorePrint.acquire()
    print(f"The secret word was: {message}")
    match(result):
        case "WIN":
            printWin()
        case "LOSE":
            printLose()
    semaphorePrint.release()
    stopPlaying()

def pringHangManWord(word, tries):
    print( "______    ")
    match(tries):
        case 0:
            print( "|         ")
            print( "|         ")
            print(f"|         {word}")
        case 1:
            print( "|    0    ")
            print( "|         ")
            print(f"|         {word}")
        case 2:
            print( "|    0    ")
            print( "|    |    ")
            print(f"|         {word}")
        case 3:
            print( "|    0    ")
            print( "|   -|    ")
            print(f"|         {word}")
        case 4:
            print( "|    0    ")
            print( "|   -|-   ")
            print(f"|         {word}")
        case 5:
            print( "|    0    ")
            print( "|   -|-   ")
            print(f"|   /     {word}")
        case 6:
            print( "|    0    ")
            print( "|   -|-   ")
            print(f"|   / \   {word}")


def play(opponent, addressOponent):
    global playing, wasInvitedToPlay, recivedGameOver
    semaphorePlaying.acquire()
    playing = True
    if clientInititedTheGame:
        semaphorePrint.acquire()
        secretWord = input("Type the secret word: ")
        semaphorePrint.release()

        lettersMissing = returnLenWord(secretWord)
        letters = []
        tries = 0
        recievedMessage = ''

        while playing:
            if not wasInvitedToPlay:
                option = getOptionGame(clientInititedTheGame)
                match(option):
                    case 1:
                        recievedMessage = sendReceiveMessage(
                            f"GAME {tries} {returnWordLettersFound(secretWord, letters)}", addressOponent, False, False)
                        if (len(recievedMessage) == 1):
                            if recievedMessage not in letters:
                                letters.append(recievedMessage)
                            if lettersMissing > returnLettersMissing(secretWord, letters):
                                lettersMissing = returnLettersMissing(
                                    secretWord, letters)
                                if (lettersMissing == 0):
                                    opponentWin(addressOponent, secretWord)
                            else:
                                tries += 1
                        else:
                            if recievedMessage == secretWord:
                                opponentWin(addressOponent, secretWord)
                            else:
                                tries += 1
                        if (tries >= 6):
                            opponentLose(addressOponent, secretWord)
                    case 2:
                        stopPlaying()
        if (tries < 6 and lettersMissing != 0 and recievedMessage != secretWord):
            if not recivedGameOver:
                sendGameOver(addressOponent)
            recivedGameOver = False
            printGameOver(opponent)
    else:
        recievedMessage = ''
        while playing:
            if not wasInvitedToPlay:
                recievedMessage = recieveMessage("GAME", False)
                if recievedMessage != "Message Error":
                    if (getFirstWord(recievedMessage) != "WIN" and getFirstWord(recievedMessage) != "LOSE"):
                        tries = int(getFirstWord(recievedMessage))
                        recievedMessage = excludeFirstWord(recievedMessage)
                        pringHangManWord(recievedMessage, tries)
                        semaphorePrint.acquire()
                        option = getOptionGame(clientInititedTheGame)
                        processOptionGame(option, addressOponent)
                        semaphorePrint.release()
                    else:
                        processResult(recievedMessage)
        if (getFirstWord(recievedMessage) != "WIN" and getFirstWord(recievedMessage) != "LOSE"):
            if not recivedGameOver:
                sendGameOver(addressOponent)
            recivedGameOver = False
            printGameOver(opponent)

    # semaphorePrint.acquire()
    # print(f"Another match was accepted. The match with {opponent} is over.")
    # semaphorePrint.release()
    semaphorePlaying.release()
    return


def printOptions():
    print("Choose a option:")
    print("1. LIST-USER-ON-LINE")
    print("2. LIST-USER-PLAYING")
    print("3. PLAY")
    print("9. DISCONNECT")


def printInvalid():
    print("Invalid values, try again")

def getOption():
    printOptions()
    try:
        return int(input("Option: "))
    except:
        printInvalid()
        return getOption()


def getPort():
    try:
        port = int(input("Plese, type a number port greater than 1024: "))
        if port < 1024:
            raise ValueError
        return port
    except:
        printInvalid()
        return getPort()


idMessage = 0
idSemaphone = Semaphore(1)
semaphorePrint = Semaphore(1)
semaphorePlaying = Semaphore(1)

serverPort = getPort()
sock = socket(AF_INET, SOCK_DGRAM)
sock.bind(("", serverPort))
sock.settimeout(5)

wasInvitedToPlay = False
recivedGameOver = False
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
                    if addressOponent != '':
                        play(opponent, addressOponent)
                case 9:
                    connected = False
                case _:
                    printInvalid()
                    semaphorePrint.release()
            printSeparator()
    sock.close()
    exit(0)


if __name__ == "__main__":
    main()

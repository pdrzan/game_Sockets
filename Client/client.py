from ipaddress import ip_address
from multiprocessing.connection import wait
import time
from socket import *
import threading
from threading import *

serverIpAddrees = ''


def printGameOver():
    print(f"The game with game is over")


def printGameOptions(youInvited):
    print("Choose a option:")
    if not youInvited:
        print("1. Guess a letter")
        print("2. Guess the word")
        print("3. Quit the game")
    else:
        print("1. Continue playing")
        print("2. Quit the game")


def printWin():
    print("You won, Congrats!")


def printLose():
    print("You losed, maybe next time...")


def printHangManWord(word, tries):
    print("______    ")
    if (tries == '0'):
        print("|         ")
        print("|         ")
        print(f"|         {word}")
    elif (tries == '1'):
        print("|    0    ")
        print("|         ")
        print(f"|         {word}")
    elif (tries == '2'):
        print("|    0    ")
        print("|    |    ")
        print(f"|         {word}")
    elif (tries == '3'):
        print("|    0    ")
        print("|   -|    ")
        print(f"|         {word}")
    elif (tries == '4'):
        print("|    0    ")
        print("|   -|-   ")
        print(f"|         {word}")
    elif (tries == '5'):
        print("|    0    ")
        print("|   -|-   ")
        print(f"|   /     {word}")
    elif (tries == '6'):
        print("|    0    ")
        print("|   -|-   ")
        print(f"|   / \   {word}")


def printSeparator(message=''):
    if message != '':
        print(message)
    print("=" * 50)


def printInvalid():
    print("Invalid values, try again")


def printOptions():
    print("Choose a option:")
    print("1. LIST-USER-ON-LINE")
    print("2. LIST-USER-PLAYING")
    print("3. PLAY")
    print("4. WAIT AN INVITATION")
    print("9. DISCONNECT")


def bytesToString(message):
    return message.decode('utf-8')


def stringToBytes(message):
    return bytes(message, "utf-8")


def addressStrintToAddressTuple(addressString):
    return (addressString.split()[0], int(addressString.split()[1]))


def sendMessage(socket, message, address, idMessage=''):
    if idMessage != '':
        message = f"{idMessage} {message}"
    socket.sendto(stringToBytes(message), address)


def recieveMessage(idMessage, recievedMessages):
    while idMessage not in recievedMessages:
        time.sleep(0.3)
    return recievedMessages.pop(idMessage)


def addMessage(idMessage, message, addressMessage, recivedMessages):
    recivedMessages[idMessage] = [
        message[len(idMessage) + 1:],
        addressMessage
    ]


def reciveMessages(socket, recivedMessages):
    try:
        while 1:
            message, addressMessage = socket.recvfrom(1024)
            message = bytesToString(message)
            idMessage = getFirstWord(message)
            addMessage(idMessage, message, addressMessage, recivedMessages)
    except:
        return


def getPort():
    try:
        port = int(input("Plese, type a number port greater than 1024: "))
        if port < 1024:
            raise ValueError
        return port
    except:
        printInvalid()
        return getPort()


def getLoginInformation():
    name = input("Name: ")
    user = input("User: ")
    password = input("Password: ")
    return name, user, password


def getInviteResponse(opponent):
    print(f"The user {opponent} invited you to a game")
    response = input("Type 'y' to accept and any other key to decline: ")
    return response == 'y'


def getOption():
    printOptions()
    try:
        return int(input("Option: "))
    except:
        printInvalid()
        return getOption()


def getOptionGame(youInvited):
    printGameOptions(youInvited)
    try:
        return int(input("Option: "))
    except:
        printInvalid()
        return getOptionGame(youInvited)


def getFirstWord(message):
    return message.split()[0]


def getOpponent():
    return input("Type the user you want to play with or: ")


def getSecretWord():
    return input("Type the secret word: ")


def getLetter():
    try:
        letter = input("Type a letter: ")
        if len(letter) != 1 or not letter.isalpha():
            raise ValueError
        return letter
    except:
        printInvalid()
        return getLetter()


def getWord():
    try:
        word = input("Type a word: ")
        if not word.replace(' ', '').isalpha():
            raise ValueError
        return word
    except:
        printInvalid()
        return getWord()


def getUserInformation(socket, recievedMessages, user, opponent):
    sendMessage(socket, f'userInformation {user} {opponent}',
                (serverIpAddrees, 12000), idMessage='SERVER')
    recievedMessage, address = recieveMessage('SERVER', recievedMessages)
    return recievedMessage


def listUserOnline(socket, recievedMessages, user):
    sendMessage(socket, f'listOnline {user}',
                (serverIpAddrees, 12000), idMessage='SERVER')
    recievedMessage, address = recieveMessage('SERVER', recievedMessages)
    print(recievedMessage)


def listUserPlaying(socket, recievedMessages, user):
    sendMessage(socket, f'listPlaying {user}',
                (serverIpAddrees, 12000), idMessage='SERVER')
    recievedMessage, address = recieveMessage('SERVER', recievedMessages)
    print(recievedMessage)


def inviteToPlay(socket, recievedMessages, user, opponent):
    addressOpponent = getUserInformation(
        socket, recievedMessages, user, opponent)
    addressOpponent = addressStrintToAddressTuple(addressOpponent)
    if addressOpponent != "Opponent not found":
        sendMessage(socket, f'GAME_INI {user}', addressOpponent, 'CLIENT_INV')
        recievedMessage, address = recieveMessage(
            'CLIENT_INVRES', recievedMessages)
        if recievedMessage == 'GAME_ACK':
            return True, addressOpponent
    return False, ''


def invitedToPlay(socket, recievedMessages):
    recievedMessage, addressOpponent = recieveMessage(
        'CLIENT_INV', recievedMessages)
    opponent = recievedMessage.split()[1]
    if getInviteResponse(opponent):
        sendMessage(socket, 'GAME_ACK', addressOpponent, 'CLIENT_INVRES')
        return True, addressOpponent, opponent
    else:
        sendMessage(socket, 'GAME_DEC', addressOpponent, 'CLIENT_INVRES')
        return False, '', ''


def removeGameMessages(recievedMessages):
    while 'GAME' in recievedMessages:
        recieveMessage('GAME', recievedMessages)


def recievedGameOver(recievedMessages):
    recieveMessage('GAME_OVER', recievedMessages)
    removeGameMessages(recievedMessages)


def sendGameOver(socket, addressOpponent):
    sendMessage(socket, '', addressOpponent, 'GAME_OVER')


def sendGameMessage(socket, message, addressOpponent):
    sendMessage(socket, message, addressOpponent, 'GAME')


def recieveGameMessage(recievedMessages):
    recievedMessage, address = recieveMessage('GAME', recievedMessages)
    return recievedMessage


def sendGameWon(socket, addressOpponent, secretWord):
    sendMessage(socket, f"WON {secretWord}", addressOpponent, 'GAME')


def sendGameLose(socket, addressOpponent, secretWord):
    sendMessage(socket, f"LOSE {secretWord}", addressOpponent, 'GAME')


def sendUsersPlaying(socket, user, opponent):
    sendMessage(socket, f"playing {user} {opponent}",
                (serverIpAddrees, 12000), idMessage='SERVER')


def sendUsersStopPlaying(socket, user, opponent):
    sendMessage(socket, f"stopPlaying {user} {opponent}",
                (serverIpAddrees, 12000), idMessage='SERVER')


def sendDisconnect(socket, user):
    sendMessage(socket, f"disconnect {user}",
                (serverIpAddrees, 12000), idMessage='SERVER')


def createSocket():
    port = getPort()
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind(("", port))
    return sock


def login(socket, idMessage, recievedMessages):
    recievedMessage = ''
    while recievedMessage != "Successfully authenticated":
        printSeparator("Login in:")
        name, user, password = getLoginInformation()
        sendMessage(socket, f"login {name} {user} {password}",
                    (serverIpAddrees, 12000), idMessage=idMessage)

        recievedMessage, address = recieveMessage(idMessage, recievedMessages)
        print(recievedMessage)
    return user


def returnLettersMissing(word, letters):
    count = 0
    word = word.replace(' ', '')
    for letter in word:
        if letter not in letters:
            count += 1
    return count


def returnWordLettersFound(word, letters):
    wordLetterFound = ''
    for letter in word:
        if letter == ' ':
            wordLetterFound += ' '
        elif letter in letters:
            wordLetterFound += letter
        else:
            wordLetterFound += '_'
    return wordLetterFound


def main():
    def resetGamesVariables():
        nonlocal playing, addressOpponent, youInvited, secretWord, lettersTried, opponent, lettersMissing
        playing = False
        youInvited = False
        addressOpponent = ''
        opponent = ''
        secretWord = ''
        lettersTried = []
        lettersMissing = 0

    recievedMessages = {}

    # achando o servidor
    global serverIpAddrees
    serverIpAddrees = input("Digite o endereço do servidor: ")

    socket = createSocket()
    myThread = threading.Thread(
        target=reciveMessages, args=(socket, recievedMessages))
    myThread.daemon = True
    myThread.start()

    user = login(socket, 'SERVER', recievedMessages)
    playing = False
    youInvited = False
    addressOpponent = ''

    secretWord = ''
    lettersTried = []
    lettersMissing = 0
    wrongTries = 0
    opponent = ''

    while 1:
        if 'CLIENT_INV' in recievedMessages:
            response, possibleAddressOpponent, possibleOpponent = invitedToPlay(
                socket, recievedMessages)
            if response:
                if playing:
                    printGameOver()
                    sendGameOver(socket, addressOpponent)
                    if youInvited:
                        sendUsersStopPlaying(socket, user, opponent)
                resetGamesVariables()
                playing = True
                addressOpponent = possibleAddressOpponent
                opponent = possibleOpponent
        elif 'GAME_OVER' in recievedMessages:
            recievedGameOver(recievedMessages)
            if youInvited:
                sendUsersStopPlaying(socket, user, opponent)
            printGameOver()
            resetGamesVariables()
        elif playing:
            if youInvited:
                if secretWord == '':
                    secretWord = getSecretWord()
                    lettersMissing = returnLettersMissing(
                        secretWord, lettersTried)
                if lettersMissing == 0:
                    sendGameWon(socket, addressOpponent, secretWord)
                    sendUsersStopPlaying(socket, user, opponent)
                    printLose()
                    resetGamesVariables()
                elif wrongTries > 6:
                    sendGameLose(socket, addressOpponent, secretWord)
                    sendUsersStopPlaying(socket, user, opponent)
                    printWin()
                    resetGamesVariables()
                else:
                    printHangManWord(returnWordLettersFound(
                        secretWord, lettersTried), f'{wrongTries}')
                    option = getOptionGame(youInvited)
                    if (option == 1):
                        sendGameMessage(
                            socket, f'{returnWordLettersFound(secretWord, lettersTried)} {wrongTries}', addressOpponent)
                        recievedMessage = recieveGameMessage(
                            recievedMessages)
                        if len(recievedMessage) == 1:
                            if recievedMessage not in lettersTried:
                                lettersTried.append(recievedMessage)
                            if lettersMissing > returnLettersMissing(secretWord, lettersTried):
                                lettersMissing = returnLettersMissing(
                                    secretWord, lettersTried)
                            else:
                                wrongTries += 1
                        else:
                            if recievedMessage == secretWord:
                                lettersMissing = 0
                            else:
                                wrongTries += 1
                    elif (option == 2):
                        sendGameMessage(
                            socket, f'{returnWordLettersFound(secretWord, lettersTried)} {wrongTries}', addressOpponent)
                        sendGameOver(socket, addressOpponent)
                        sendUsersStopPlaying(socket, user, opponent)
                        printGameOver()
                        resetGamesVariables()
            else:
                recievedMessage = recieveGameMessage(recievedMessages)
                if getFirstWord(recievedMessage) == 'WON':
                    print(
                        f'The secret word was {recievedMessage.replace("WON ", "")}')
                    resetGamesVariables()
                    printWin()
                elif getFirstWord(recievedMessage) == 'LOSE':
                    print(
                        f'The secret word was {recievedMessage.replace("LOSE ", "")}')
                    resetGamesVariables()
                    printLose()
                else:
                    printHangManWord(recievedMessage.replace(
                        ' ' + recievedMessage.split()[-1], ''), recievedMessage.split()[-1])
                    option = getOptionGame(youInvited)
                    if (option == 1):
                        letter = getLetter()
                        sendGameMessage(socket, letter, addressOpponent)
                    elif (option == 2):
                        word = getWord()
                        sendGameMessage(socket, word, addressOpponent)
                    elif (option == 3):
                        sendGameMessage(socket, '', addressOpponent)
                        sendGameOver(socket, addressOpponent)
                        printGameOver()
                        resetGamesVariables()
        else:
            option = getOption()
            if (option == 1):
                listUserOnline(socket, recievedMessages, user)
            elif (option == 2):
                listUserPlaying(socket, recievedMessages, user)
            elif (option == 3):
                opponent = getOpponent()
                playing, addressOpponent = inviteToPlay(
                    socket, recievedMessages, user, opponent)
                if playing:
                    youInvited = True
                    sendUsersPlaying(socket, user, opponent)
                else:
                    print("The opponent was not found or your invitation was rejected")
            elif (option == 4):
                print("waiting ", end="")
                time.sleep(0.5)
                print(".", end="")
                time.sleep(0.5)
                print(".", end="")
                time.sleep(0.5)
                print(".", end="")
                time.sleep(0.5)
                print(".", end="")
                time.sleep(0.5)
                print(".")
            elif (option == 9):
                sendDisconnect(socket, user)
                break
            else:
                printInvalid()
        printSeparator()
    socket.close()
    return


if __name__ == "__main__":
    main()

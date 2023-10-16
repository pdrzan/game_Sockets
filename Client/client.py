import sys, time
from socket import *

sock = socket(AF_INET, SOCK_DGRAM)
sock.connect(('',12000))
sock.settimeout(5)

def login(name, user, password):
    msg = f"login {name} {user} {password}"
    sock.send(bytes(msg, "utf-8"))
    return sock.recv(1024)

def printOptions():
    print("Escolha uma opcao:")
    print("1. LIST-USER-ON-LINE")
    print("2. LIST-USER-PLAYING")
    print("3. PLAY")
    print("9. DISCONECTAR")

def main():
    print("Para começarmos é necesssário fazer o login")
    name = input("Digite seu nome:")
    user = input("Digite seu usuário:")
    password = input("Digite sua senha:")
    login(name, user, password)
    connected = True
    while connected:
        printOptions()
        option = int(input())
        match(option):
            case 9:
                connected = False
        
from socket import *
import account
import pickle
import sys

myAccount = account.Account
serverName = "inputIpAddressHere"
serverPort = 31000
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))
while True:
    request = input("1. Log In\n2. Sign Up\n3. Quit")
    if request == 1:
        while True:
            userName = input("Please enter a user name you like or q or quit")
            clientSocket.sendall(pickle.dumps("logIn********"+userName))
            createdAcc = pickle.loads(clientSocket.recv(4028))
            if(createdAcc == "UsernameTaken"):
                print("That username is taken")
            else:
                myAccount = createdAcc

    elif request == 2:
        print("")
    elif request == 3:
        print("Good bye")
        break
    else:
        print("Please enter a valid option")
    

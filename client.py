from socket import *
import account
import pickle

myAccount = account.Account()
serverName = "196.47.227.102"
serverPort = 14000
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))
while True:
    request = input("1. Sign Up\n2. Log In\n3. Quit\n")
    print(request)

    #Sign Up
    if request == "1":
        while True:
            userName = input("Please enter a user name you like or q to quit\n")
            clientSocket.sendall(pickle.dumps("SignUp*******"+userName))
            createdAcc = pickle.loads(clientSocket.recv(4028))
            print("client" + createdAcc.accUsername)
            if(createdAcc.accUsername != userName):
                print("That username is taken\n")
            else:
                myAccount = createdAcc
                print("Account created your username is:\n"+myAccount.accUsername)

    elif request == "2":
        print("")
    elif request == "3":
        print("Good bye")
        break
    else:
        print("Please enter a valid option\n")
    

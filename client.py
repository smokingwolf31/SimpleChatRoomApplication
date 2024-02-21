from socket import *
import account
import pickle

myAccount = account.Account()
serverName = "196.47.227.102"
serverPort = 14000
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

def signUp():
    while True:
        userName = input("Please enter a user name you like or q to quit\n")
        if userName == "q":
            break
        clientSocket.sendall(pickle.dumps("SignUp*******"+userName))
        createdAcc = pickle.loads(clientSocket.recv(4028))
        if(createdAcc.accUsername != userName):
            print("That username is taken\n")
        else:
            myAccount = createdAcc
            print("Account created your username is:\n"+myAccount.accUsername)

def logIn():
    print("to be completed")

def listOnlineAccounts():
    print("to be completed")   

def main():
    while True:
        request = input("1. Sign Up\n2. Log In\n3. Quit\n")
    
        #Sign Up
        if request == "1":
            signUp()

        elif request == "2":
            logIn()
        elif request == "3":
            print("Good bye")
            break
        else:
            print("Please enter a valid option\n")

if __name__ == "__main__":
    main()
    

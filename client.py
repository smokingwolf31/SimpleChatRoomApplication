from socket import *
import account
import pickle

myAccount = account.Account(accUsername="spaceHolder", status=account.Status.OFFLINE)
serverName = "196.47.227.102"
serverPort = 14000
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

def signUp():
    while True:
        global myAccount
        userName = input("Please enter a user name you like or q to quit\n")
        if userName == "q":
            break
        myAccount.accUsername = userName
        clientSocket.sendall(pickle.dumps("SignUp*******"))
        clientSocket.sendall(pickle.dumps(myAccount))
        createdAcc = pickle.loads(clientSocket.recv(4028))
        if(createdAcc.status == account.Status.OFFLINE):
            print("That username is taken\n")
        else:
            myAccount = createdAcc
            print("Account created your username is:\n"+myAccount.accUsername)
            break
            

def logIn():
    global myAccount
    clientSocket.sendall(pickle.dumps("LogIn********"))
    while True:
        userName = input("Please enter your username or q to quit\n")
        if (userName == "q"):
            break
        myAccount.accUsername = userName
        clientSocket.sendall(pickle.dumps(myAccount))
        myAccount = pickle.loads(clientSocket.recv(4028))
        if (myAccount.status == account.Status.ONLINE):
            print("Welcome back" + myAccount.accUsername+"\n")
            break
        else:
            print("Account not found !!\n")

def logOut():
    clientSocket.sendall(pickle.dumps("LogOut*******"))
    clientSocket.sendall(pickle.dumps(myAccount))
    clientSocket.close()
    print("It was nice having you :)")

def listOnlineAccounts():
    clientSocket.sendall(pickle.dumps("WhoIsOnline**"))
    onlineUsers = pickle.loads(clientSocket.recv(4028))
    if onlineUsers:
        for accUsername in onlineUsers:
            print(accUsername)
    else:
        print("No online users at the moment")

def main():
    while True:
    
        #Sign Up
        if(myAccount.status == account.Status.OFFLINE):
            request = input("1. Sign Up\n2. Log In\n")
            if request == "1":
                signUp()

            elif request == "2":
                logIn()
        else:
            request = input("1. List Online People\n2. Log Out")
            if request == "1":
                listOnlineAccounts()
            elif request == "2":
                logOut()
                break

if __name__ == "__main__":
    main()
    

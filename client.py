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
        clientSocket.sendall(pickle.dumps("SignUp*******"))
        clientSocket.sendall(pickle.dumps(userName))
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
        clientSocket.sendall(pickle.dumps(userName))
        myAccount = pickle.loads(clientSocket.recv(4028))
        if (myAccount.status == account.Status.ONLINE):
            print("Welcome back" + myAccount.accUsername+"\n")
            break
        else:
            print("Account not found !!\n")

def handlePeerToPeerConvo(usernameToSendTo):
    clientSocket.sendall(pickle.dumps("ConnectToAcc*"))
    clientSocket.sendall(pickle.dumps(usernameToSendTo))
    peerSocket = pickle.loads(clientSocket.recv(4028))
    peerAddress, peerPort = peerSocket.getsockname()
    peerSocketUDP = socket(AF_INET, SOCK_DGRAM)

def handleInbox():
    while True:
        usernameToSendTo = input("Please enter thier username (q to exit)")
        if (usernameToSendTo == "q"):
            break
        clientSocket.sendall(pickle.dumps("DoesUserExist"))
        clientSocket.sendall(pickle.dumps(usernameToSendTo))
        userExist = pickle.loads(clientSocket.recv(4028))
        if (userExist):
            clientSocket.sendall(pickle.dumps("IsUserOnline*"))
            userOnline = pickle.loads(clientSocket.recv(4028))
            if (userOnline):
                handlePeerToPeerConvo(usernameToSendTo)
            else:
                message = input("Enter your message:\n")
                clientSocket.sendall(pickle.dumps("MsgOfflineAcc"))
                clientSocket.sendall(pickle.dumps(myAccount.accUsername))
                clientSocket.sendall(pickle.dumps(usernameToSendTo))
                clientSocket.sendall(pickle.dumps(message))
                if myAccount.inbox.get(usernameToSendTo) is not None:
                    myAccount.inbox[usernameToSendTo].append(message)
                else:
                    myAccount.inbox[usernameToSendTo] = [message]
            break

        else:
            print("An account with that username was Not Found\n")

def listOnlineAccounts():
    clientSocket.sendall(pickle.dumps("WhoIsOnline**"))
    onlineUsers = pickle.loads(clientSocket.recv(4028))
    if onlineUsers:
        for accUsername in onlineUsers:
            print(accUsername)
    else:
        print("No online users at the moment\n")

def logOut():
    clientSocket.sendall(pickle.dumps("LogOut*******"))
    clientSocket.sendall(pickle.dumps(myAccount))
    clientSocket.close()
    print("It was nice having you :)\n")

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
                print("Please enter a valid option\n")
        else:
            request = input("1. Inbox\n2. List Online People\n3. Log Out\n")
            if request == "1":
                handleInbox()

            elif request == "2":
                listOnlineAccounts()
            elif request == "3":
                logOut()
                break
            else:
                print("Please enter a valid option\n")

if __name__ == "__main__":
    main()
    

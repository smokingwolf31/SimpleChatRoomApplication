from socket import *
import threading
import account
import message as msg
import pickle
import select
import os

myAccount = account.Account(accUsername="spaceHolder", status=account.Status.OFFLINE)
serverName = "196.47.227.102"
serverPort = 15040

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

peerSocket = socket(AF_INET, SOCK_DGRAM)

def printInbox(username):
    if myAccount.inbox.get(username) is not None:
        currentInbox = myAccount.inbox[username]
        for textMessage in currentInbox:
            print(textMessage)

def clearTerminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def signUp():
    while True:
        global myAccount
        userName = input("Please enter a user name you like or q to quit\n").strip()
        messageToSend = msg.Message() #sent messageToSend.text = usernName
        if userName == "q":
            break
        messageToSend.request = "SignUp*******"
        messageToSend.text = userName
        clientSocket.sendall(pickle.dumps(messageToSend))
        accSent = (pickle.loads(clientSocket.recv(4028))).account
        if(accSent.status == account.Status.OFFLINE):
            print("That username is taken\n")
        else:
            myAccount = accSent
            print("Account created your username is:\n"+myAccount.accUsername)
            peerSocket.bind(('',myAccount.port))
            inboxRecivindThread.start()
            break
            

def logIn():
    global myAccount
    while True:
        userName = input("Please enter your username or q to quit\n")
        if (userName == "q"):
            break
        messageToSend = msg.Message()
        messageToSend.request = "LogIn********"
        messageToSend.text = userName
        clientSocket.sendall(pickle.dumps(messageToSend))
        myAccount = pickle.loads(clientSocket.recv(4028)).account
        if (myAccount.status == account.Status.ONLINE):
            print("Welcome back" + myAccount.accUsername+"\n")
            peerSocket.bind(('',myAccount.port))
            inboxRecivindThread.start()
            break
        else:
            print("Account not found !!\n")

def handleOnlineInbox(clientSocket, usernameToSendTo, actualMessageFromOfflineHandle):
    messageToSend = msg.Message()
    messageToSend.request = "ConnectToAcc*"
    messageToSend.text = usernameToSendTo
    clientSocket.sendall(pickle.dumps(messageToSend))
    messageRecieved = pickle.loads(clientSocket.recv(4028))
    peerAddress = messageRecieved.ipAddress
    peerPort = messageRecieved.portNumber
    peerSocketUDP = socket(AF_INET, SOCK_DGRAM)
    messageToSend.request = myAccount.accUsername
    stillOnline = True
    actualMessage = ""
    while True:
        messageToSend.request = "IsUserOnline*"
        messageToSend.text = usernameToSendTo
        clientSocket.sendall(pickle.dumps(messageToSend))
        stillOnline = pickle.loads(clientSocket.recv(4028)).result
        if not stillOnline:
            handleOfflineInbox(clientSocket, usernameToSendTo, actualMessage)
            break
        clearTerminal()
        print(usernameToSendTo + " ** Online **\n")
        print ("Enter your message or Quit** to exit\n\n")
        printInbox(usernameToSendTo)
        if actualMessageFromOfflineHandle !=  None:
            actualMessage = actualMessageFromOfflineHandle
            actualMessageFromOfflineHandle = None
        else:
            actualMessage = input(myAccount.accUsername+": ")
        if actualMessage == "Quit**":
            peerSocketUDP.close()
            return
        messageToSend.request = myAccount.accUsername
        messageToSend.text = actualMessage
        peerSocketUDP.connect((peerAddress, peerPort))
        peerSocketUDP.sendall(pickle.dumps(messageToSend))
        print(myAccount.accUsername+ ": " +actualMessage)
        if myAccount.inbox.get(usernameToSendTo) is None:
            myAccount.inbox[usernameToSendTo] = []
        myAccount.inbox[usernameToSendTo].append(myAccount.accUsername+ ":" +actualMessage)



def handleOfflineInbox(clientSocket, usernameToSendTo, actualMessageFromOnlineHandle):
    printInbox(usernameToSendTo)
    actualMessage = ""
    messageToSend = msg.Message()
    while True:
        messageToSend.request = "IsUserOnline*"
        messageToSend.text = usernameToSendTo
        clientSocket.sendall(pickle.dumps(messageToSend))
        userOnline = pickle.loads(clientSocket.recv(4028)).result
        if userOnline:
            handleOnlineInbox(clientSocket, usernameToSendTo, actualMessage)
            break
        clearTerminal()
        print(usernameToSendTo + " ** Offline **\n")
        print ("Enter your message or Quit** to exit\n\n")
        printInbox(usernameToSendTo)
        if actualMessageFromOnlineHandle !=  None:
            actualMessage = actualMessageFromOnlineHandle
            actualMessageFromOnlineHandle = None
        else:
            actualMessage = input(myAccount.accUsername+": ")
        if(actualMessage == "Quit**"):
            return
        messageToSend.request = "MsgOfflineAcc"
        messageToSend.text = myAccount.accUsername + " " + usernameToSendTo + " " + actualMessage 
        clientSocket.sendall(pickle.dumps(messageToSend))
        if myAccount.inbox.get(usernameToSendTo) is None:
            myAccount.inbox[usernameToSendTo] = []
        myAccount.inbox[usernameToSendTo].append(myAccount.accUsername+ ": " +actualMessage)


def handleInbox():
    global myAccount
    while True:
        usernameToSendTo = input("Please enter their username (q to exit)\n")
        if (usernameToSendTo == "q"):
            break
        if (usernameToSendTo == myAccount.accUsername):
            print("Enter an username beside your own\n")
            continue
        messageToSend = msg.Message()
        messageToSend.request = "DoesUserExist"
        messageToSend.text = usernameToSendTo
        clientSocket.sendall(pickle.dumps(messageToSend))
        userExist = pickle.loads(clientSocket.recv(4028)).result
        if (userExist):
            myAccount.currentlyInbox = usernameToSendTo
            messageToSend.request = "IsUserOnline*"
            clientSocket.sendall(pickle.dumps(messageToSend))
            userOnline = pickle.loads(clientSocket.recv(4028)).result
            clearTerminal()
            if (userOnline):
                handleOnlineInbox(clientSocket, usernameToSendTo, None)
            else:
                handleOfflineInbox(clientSocket, usernameToSendTo, None)
            myAccount.currentlyInbox = ""
            break

        else:
            print("An account with that username was Not Found\n")
            continue

def handleReceivedInbox(peerSocket):
    peerSocket.settimeout(1)
    while myAccount.status == account.Status.ONLINE:
        try:
            readable, _, _ = select.select([peerSocket], [], [], 1)

            if readable:
                data, _ = peerSocket.recvfrom(2048)
                messageReceived = pickle.loads(data)
                messageSent = messageReceived.text
                sender = messageReceived.request
                if(sender == myAccount.currentlyInbox):
                    clearTerminal()
                    print(sender + " ** Online **\n")
                    print ("Enter your message or Quit** to exit\n\n")
                    printInbox(sender)
                    print(sender + ": " + messageSent)
                if myAccount.inbox.get(sender) is None:
                    myAccount.inbox[sender] = []
                myAccount.inbox[sender].append(sender + ": "+ messageSent)
        except Exception as e:
            print(e)



def listOnlineAccounts():
    clearTerminal()
    messageToSend = msg.Message()
    messageToSend.request = "WhoIsOnline**"
    clientSocket.sendall(pickle.dumps(messageToSend))
    onlineUsers = pickle.loads(clientSocket.recv(4028)).arrayToSend
    if onlineUsers:
        print("User who are online:\n")
        for accUsername in onlineUsers:
            print(accUsername)
    else:
        print("No online users at the moment\n")

def logOut():
    myAccount.status = account.Status.OFFLINE
    messageToSend = msg.Message()
    messageToSend.request = "LogOut*******"
    messageToSend.account = myAccount
    clientSocket.sendall(pickle.dumps(messageToSend))
    clientSocket.close()
    peerSocket.close()

    print("It was nice having you :)\n")

inboxRecivindThread = threading.Thread(target=handleReceivedInbox, args=(peerSocket,))

def main():
    while True:
        #Sign Up
        if(myAccount.status == account.Status.OFFLINE):
            clearTerminal()
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
                clearTerminal()
                logOut()
                break
            else:
                print("Please enter a valid option\n")

if __name__ == "__main__":
    main()
    

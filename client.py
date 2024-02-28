from socket import *
import threading
import account
import message as msg
import pickle
import select
import sys
import os

myAccount = account.Account(accUsername="spaceHolder", status=account.Status.OFFLINE)
serverName = ""
serverPort = -1

clientSocket = socket(AF_INET, SOCK_STREAM)
peerSocket = socket(AF_INET, SOCK_DGRAM)

# Used to print the current inbox between the user and the spicified contact
def printPrivateInbox(username):
    if myAccount.privateInbox.get(username) is not None:
        currentInbox = myAccount.privateInbox[username]
        for textMessage in currentInbox:
            print(textMessage)

# Used to print the current inbox between the user and the specified group inbox
def printGroupInbox(groupName):
    if myAccount.groupInbox.get(groupName) is not None:
        currentInbox = myAccount.groupInbox[groupName]
        for textMessage in currentInbox:
            print(textMessage)

# Clears the everthing written on the terminal
def clearTerminal():
    os.system('cls' if os.name == 'nt' else 'clear')

# Handles the signing up of clients. (THat is makes sure the user has an account an the server knows of this account)
def signUp():
    while True:
        global myAccount
        userName = input("Please enter a user name you like or q to quit\n").strip()
        messageToSend = msg.Message() #sent messageToSend.text = usernName
        if userName == "q":
            break
        if " " in userName:
            clearTerminal()
            print("\n***No spaces are allowed in your username***\n\n")
            continue
        password = input("Please input your preferred password\n")
        messageToSend.request = "SignUp*******"
        messageToSend.text = userName + " " + password
        clientSocket.sendall(pickle.dumps(messageToSend))
        accSent = (pickle.loads(clientSocket.recv(4028))).account
        if(accSent.status == account.Status.OFFLINE):
            clearTerminal()
            print("\n***That username is taken***\n\n")
        else:
            myAccount = accSent
            peerSocket.bind(('',myAccount.port))
            inboxRecivindThread.start()
            break
            

# Used to log in a user. Gets the saved user account from the server
def logIn():
    global myAccount
    while True:
        userName = input("Please enter your username or q to quit\n")
        if (userName == "q"):
            break
        if " " in userName:
            clearTerminal()
            print("Please enter a valid username (no spaces)")
            continue
        password = input("Please enter your password or q to quit\n")
        messageToSend = msg.Message()
        messageToSend.request = "LogIn********"
        messageToSend.text = userName + " " + password
        clientSocket.sendall(pickle.dumps(messageToSend))
        myAccount = pickle.loads(clientSocket.recv(4028)).account
        if (myAccount.status == account.Status.ONLINE):
            peerSocket.bind(('',myAccount.port))
            inboxRecivindThread.start()
            break
        else:
            print("Incorect username or password!!\n")

# Used to continously 
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
        print ("Enter your message or (Attach** for file sending and Quit** to exit)\n\n")
        printPrivateInbox(usernameToSendTo)
        if actualMessageFromOfflineHandle !=  None:
            actualMessage = actualMessageFromOfflineHandle
            actualMessageFromOfflineHandle = None
        else:
            actualMessage = input(myAccount.accUsername+": ")
        if actualMessage == "Quit**":
            peerSocketUDP.close()
            return
        elif actualMessage == "Attach**":
            clearTerminal()
            while True:
                try:
                    filePath = input("\nPlease enter the file path or Quit** to go back\n")
                    if filePath == "Quit**":
                        break
                    with open(filePath, "rb") as file:
                        messageToSend.text = "Attach** " + myAccount.accUsername + " " + filePath
                        messageToSend.fileData = file.read()
                        break
                except FileNotFoundError:
                    clearTerminal()
                    print("\nFile not found")
            continue
        else:
            messageToSend.text = "Private** "+ myAccount.accUsername + " " + actualMessage
        peerSocketUDP.connect((peerAddress, peerPort))
        print("Sending")
        peerSocketUDP.sendall(pickle.dumps(messageToSend))
        print("Sent")
        print(myAccount.accUsername+ ": " +actualMessage)
        myAccount.privateInbox.setdefault(usernameToSendTo, []).append(myAccount.accUsername+ ": " +actualMessage)



def handleOfflineInbox(clientSocket, usernameToSendTo, actualMessageFromOnlineHandle):
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
        printPrivateInbox(usernameToSendTo)
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
        myAccount.privateInbox.setdefault(usernameToSendTo, []).append(myAccount.accUsername+ ": " +actualMessage)


def handlePrivateInbox():
    global myAccount
    while True:
        myAccNames = list(myAccount.privateInbox.keys())
        for accName in myAccNames:
            print(accName+"\n")
        usernameToSendTo = input("\nPlease enter their username (q to exit)\n")
        if (usernameToSendTo == "q"):
            break
        if (usernameToSendTo == myAccount.accUsername):
            clearTerminal()
            print("Enter a username your own\n")
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
            clearTerminal()
            print("\nAn account with that username was Not Found\n")
            continue

def sendMessageToGroup(groupName):
    myAccount.currentlyInbox = groupName
    messageToSend = msg.Message()
    while True:
        clearTerminal()
        print("*** "+groupName+" ***\n")
        print("Enter your message or Quit** to exit\n\n")
        printGroupInbox(groupName)
        actualMessage = input(myAccount.accUsername+": ")
        if (actualMessage == "Quit**"):
            myAccount.currentlyInbox = ""
            break
        messageToSend.request = "SendToGroup**"
        messageToSend.text = groupName + " " + myAccount.accUsername + " " + actualMessage
        clientSocket.sendall(pickle.dumps(messageToSend))
        myAccount.groupInbox.setdefault(groupName, []).append(myAccount.accUsername + " " + actualMessage)
    myAccount.currentlyInbox = ""


def handleGroupInbox():
    global myAccount
    while True:
        myGroups = list(myAccount.groupInbox.keys())
        for groupName in myGroups:
            print(groupName+"\n")
        groupName = input("\nPlease enter the group name (q to exit)\n")
        if (groupName == "q"):
            break
        messageToSend = msg.Message()
        messageToSend.request = "DoesGroupExist"
        messageToSend.text = groupName
        clientSocket.sendall(pickle.dumps(messageToSend))
        groupExits = pickle.loads(clientSocket.recv(4028))
        if groupExits:
            if myAccount.groupInbox.get(groupName) is None:
                joinGroup = input("Do you wish to join "+groupName+" (Y/n)")
                if(joinGroup.lower() == "y"):
                    myAccount.groupInbox[groupName] = []
                    messageToSend.request = "AddToGroup***"
                    messageToSend.text = groupName + " " + myAccount.accUsername
                    clientSocket.sendall(pickle.dumps(messageToSend))
                else:
                    continue
        else:
            createGroup = input("That group does not exist would you like to create it (Y/n)")
            if createGroup.lower() == "y":
                myAccount.groupInbox[groupName] = []
                messageToSend.request = "AddToGroup***"
                messageToSend.text = groupName +" "+ myAccount.accUsername
                clientSocket.sendall(pickle.dump(messageToSend))
            else:
                continue
        sendMessageToGroup(groupName)
        


def handleReceivedInbox(peerSocket):
    peerSocket.settimeout(1)
    while myAccount.status == account.Status.ONLINE:
        try:
            readable, _, _ = select.select([peerSocket], [], [], 1)

            if readable:
                print("Somethings was sent")
                data, _ = peerSocket.recvfrom(2048)
                messageReceived = pickle.loads(data)
                messageSent = messageReceived.text
                messageType = messageSent[:messageSent.index(" ")]
                messageSent = messageSent[messageSent.index(" ")+1:]
                sender = messageSent[:messageSent.index(" ")]
                messageSent = messageSent[messageSent.index(" ")+1:]
                if messageType == "Group**":
                    groupName = messageSent[:messageSent.index(" ")]
                    messageSent = messageSent[messageSent.index(" ")+1:]
                    if groupName == myAccount.currentlyInbox:
                        clearTerminal()
                        print("** "+groupName+" **")
                        print ("Enter your message or Quit** to exit\n\n")
                        printGroupInbox(groupName)
                        print(sender + ": " + messageSent)
                    myAccount.groupInbox.setdefault(groupName, []).append(sender + ": "+ messageSent)
                elif messageType == "Private**":
                    if(sender == myAccount.currentlyInbox):
                        clearTerminal()
                        print(sender + " ** Online **\n")
                        print ("Enter your message or Quit** to exit\n\n")
                        printPrivateInbox(sender)
                        print(sender + ": " + messageSent)
                    myAccount.privateInbox.setdefault(sender, []).append(sender + ": " + messageSent)
                else:
                    print("Ifikile")
                    fileData = messageReceived.fileData
                    with open("test3.py", 'wb') as file:
                        file.write(fileData)


        except Exception as e:
            pass



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
    if myAccount.status == account.Status.ONLINE:
        messageToSend = msg.Message()
        messageToSend.request = "LogOut*******"
        myAccount.status = account.Status.OFFLINE
        messageToSend.account = myAccount
        clientSocket.sendall(pickle.dumps(messageToSend))
        myAccount.status = account.Status.OFFLINE
    clientSocket.close()
    peerSocket.close()
    sys.exit()

inboxRecivindThread = threading.Thread(target=handleReceivedInbox, args=(peerSocket,))

def main():
    serverName = sys.argv[1]
    serverPort = int(sys.argv[2])
    clientSocket.connect((serverName, serverPort))
    try:
        clearTerminal()
        while True:
            if(myAccount.status == account.Status.OFFLINE):
                request = input("1. Sign Up\n2. Log In\n3. Quit\n")
                if request == "1":
                    clearTerminal()
                    signUp()
                    clearTerminal()
                elif request == "2":
                    clearTerminal()
                    logIn()
                    clearTerminal()
                elif request == "3":
                    clearTerminal()
                    logOut()
                else:
                    print("Please enter a valid option\n")
            else:
                request = input("\nLogged in as "+myAccount.accUsername+"\n\n1. Inbox\n2. List Online People\n3. Log Out\n")
                if request == "1":
                    while True:
                        clearTerminal()
                        inboxRequest = input("\nLogged in as "+myAccount.accUsername+"\n\n1. My Contacts\n2. My Groups\n3. Back\n")
                        if inboxRequest == "1":
                            clearTerminal()
                            handlePrivateInbox()
                            clearTerminal()
                        elif inboxRequest == "2":
                            clearTerminal()
                            handleGroupInbox()
                            clearTerminal()
                        elif inboxRequest == "3":
                            clearTerminal()
                            break
                        else:
                            print("Please enter a valid input\n")

                elif request == "2":
                    clearTerminal()
                    listOnlineAccounts()
                elif request == "3":
                    clearTerminal()
                    logOut()
                    break
                else:
                    print("Please enter a valid option\n")
    except :
        logOut()

if __name__ == "__main__":
    main()
    

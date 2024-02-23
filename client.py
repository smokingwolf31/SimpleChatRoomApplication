from socket import *
import threading
import account
import message as msg
import pickle
import sys

myAccount = account.Account(accUsername="spaceHolder", status=account.Status.OFFLINE)
serverName = "196.47.231.19"
serverPort = 15033

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

peerSocket = socket(AF_INET, SOCK_DGRAM)

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
            inboxRecivindThread = threading.Thread(target=handleRecievedInbox, args=(peerSocket,))
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
            inboxRecivindThread = threading.Thread(target=handleRecievedInbox, args=(peerSocket,))
            inboxRecivindThread.start()
            break
        else:
            print("Account not found !!\n")

def handlePeerToPeerConvo(clientSocket, usernameToSendTo):
    messageToSend = msg.Message()
    messageToSend.request = "ConnectToAcc*"
    messageToSend.text = usernameToSendTo
    clientSocket.sendall(pickle.dumps(messageToSend))
    messageRecieved = pickle.loads(clientSocket.recv(4028))
    print("Recieved")
    peerAddress = messageRecieved.ipAddress
    peerPort = messageRecieved.portNumber
    peerSocketUDP = socket(AF_INET, SOCK_DGRAM)
    messageToSend.request = myAccount.accUsername
    while True:
        actualMessage = input("Enter your message or Quit** to exit")
        if actualMessage == "Quit**":
            break
        messageToSend.text = actualMessage
        peerSocketUDP.connect((peerAddress, peerPort))
        peerSocketUDP.sendall(pickle.dumps(messageToSend))
        print(myAccount.accUsername+ ": " +actualMessage)
        peerSocketUDP.close()

def handleInbox():
    global myAccount
    while True:
        usernameToSendTo = input("Please enter their username (q to exit)")
        if (usernameToSendTo == "q"):
            break
        messageToSend = msg.Message()
        messageToSend.request = "DoesUserExist"
        messageToSend.text = usernameToSendTo
        clientSocket.sendall(pickle.dumps(messageToSend))
        userExist = pickle.loads(clientSocket.recv(4028)).result
        if (userExist):
            messageToSend.request = "IsUserOnline*"
            clientSocket.sendall(pickle.dumps(messageToSend))
            userOnline = pickle.loads(clientSocket.recv(4028)).result
            if (userOnline):
                handlePeerToPeerConvo(clientSocket, usernameToSendTo)
            else:
                message = input("Enter your message:\n")
                messageToSend.request = "MsgOfflineAcc"
                messageToSend.text = myAccount.accUsername + " " + usernameToSendTo + " " + message
                clientSocket.sendall(pickle.dumps(messageToSend))
                if myAccount.inbox.get(usernameToSendTo) is not None:
                    myAccount.inbox[usernameToSendTo].append(message)
                else:
                    myAccount.inbox[usernameToSendTo] = [message]
                print("Sent to offline user")
            break

        else:
            print("An account with that username was Not Found\n")
            continue

def handleRecievedInbox(peerSocket):
    while True:
        data, serverAddress = peerSocket.recvfrom(2048)
        messageReceived = pickle.loads(data)
        messageSent = messageReceived.text
        sender = messageReceived.request
        print(sender + " :::" + messageSent)


def listOnlineAccounts():
    messageToSend = msg.Message()
    messageToSend.request = "WhoIsOnline**"
    clientSocket.sendall(pickle.dumps(messageToSend))
    onlineUsers = pickle.loads(clientSocket.recv(4028)).arrayToSend
    if onlineUsers:
        for accUsername in onlineUsers:
            print(accUsername)
    else:
        print("No online users at the moment\n")

def logOut():
    messageToSend = msg.Message()
    messageToSend.request = "LogOut*******"
    messageToSend.account = myAccount
    clientSocket.sendall(pickle.dumps(messageToSend))
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
    

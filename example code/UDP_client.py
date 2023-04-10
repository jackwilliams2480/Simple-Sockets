from socket import *
from datetime import datetime
import sys

# parse command line arguments
serverName = sys.argv[2]
serverPort = int(sys.argv[3])
resetCounter = 0
connectionID = sys.argv[4] 
resetFlag = True

# create socket datagram
clientSocket = socket(AF_INET, SOCK_DGRAM)

# Flag to handle loopback when invalid connectionID is used
while resetFlag:

    # Handle socket timeout
    try:
        message = sys.argv[1] + " " + connectionID # message + connectionID

        # send server message
        clientSocket.settimeout(15)
        clientSocket.sendto(message.encode(), (serverName, serverPort))

        # if message was recived ...
        modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
        returnCode = modifiedMessage.decode().split()

        # Handle server return code
        if(returnCode[0] == "OK"):
            response = "Connection established {} {} {} on {}".format(connectionID, serverAddress[0], serverAddress[1], datetime.now())
            print(response)
            resetFlag = False
        else:
            # If we have tried 3 times to enter a valid connectionID but still failed
            if(resetCounter > 2):
                response = "Connection failure on {}".format(datetime.now())
                print(response)
                # Trigger flag to stop loopback
                resetFlag = False
                clientSocket.close()
            else:
                response = "Connection error {} on {}".format(sys.argv[4],datetime.now())
                print(response)
                print("Please enter a new connectionID:")
                connectionID = input().strip()
                resetCounter += 1

    # If we reached the 15 second timeout period
    except timeout:
        # Since we count timeout as a "try" we check how many times we have tried the server
        if(resetCounter > 2):
            response = "Connection failure on {}".format(datetime.now())
            print(response)
            resetFlag = False
            clientSocket.close()
        else:
            response = "Connection error {} on {}".format(sys.argv[4],datetime.now())
            print(response)
            print("Please enter a new connectionID:")
            connectionID = input().strip()
            resetCounter += 1

from socket import *
from datetime import datetime
import time  
import threading
import sys

serverPort = 12000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
connID_list = []
resetCounter = 0
resetFlag = True

while resetFlag:
    

    # Handle socket timeout
    try:
        # Automatic socket timeout if server waits over 2 minutes without any connections
        serverSocket.settimeout(120)

        # Receive the client packet along with the address it is coming from
        # If the buf size value is smaller than the datagram size, it will drop the rest
        message, clientAddress = serverSocket.recvfrom(2048) 
        
        # Parse message and connectionID
        modifiedMessage = message.decode().split()
        connectionID = modifiedMessage[1]
        modifiedMessage = modifiedMessage[0]

        # Check if connectionID is already connected
        if(connectionID not in connID_list):
            # If not connected, add to connection, start timer, and return OK code
            response = "OK {} {} {}".format(connectionID, clientAddress[0], serverPort)
        
            
            connID_list.append(connectionID)
            timer = threading.Timer(30, lambda : connID_list.remove(connectionID)) # Remove connID in 30 seconds
            timer.start()
            serverSocket.sendto(response.encode(), clientAddress)

        else:

            response = "RESET {}".format(connectionID)
            serverSocket.sendto(response.encode(), clientAddress)

    except timeout:
        resetFlag = False
        # Close socket if timeout reached
        serverSocket.close()


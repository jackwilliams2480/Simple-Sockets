#!/usr/bin/env python3
# Last updated: Jan, 2023
# Author: Phuthipong (Nikko)
import sys
import socket
import datetime

CONNECTION_TIMEOUT = 60

# for testing with gaia server
SERVER_IP = "128.119.245.12"
SERVER_PORT = 20008


def checksum(msg):
    """
     This function calculates checksum of an input string
     Note that this checksum is not Internet checksum.
    
     Input: msg - String
     Output: String with length of five
     Example Input: "1 0 That was the time fo "
     Expected Output: "02018"
    """

    # step1: covert msg (string) to bytes
    msg = msg.encode("utf-8")
    s = 0
    # step2: sum all bytes
    for i in range(0, len(msg), 1):
        s += msg[i]
    # step3: return the checksum string with fixed length of five 
    #        (zero-padding in front if needed)
    return format(s, '05d')

def checksum_verifier(msg):
    """
     This function compares packet checksum with expected checksum
    
     Input: msg - String
     Output: Boolean - True if they are the same, Otherwise False.
     Example Input: "1 0 That was the time fo 02018"
     Expected Output: True
    """

    expected_packet_length = 30
    # step 1: make sure the checksum range is 30
    if len(msg) < expected_packet_length:
        return False
    # step 2: calculate the packet checksum
    content = msg[:-5]
    calc_checksum = checksum(content)
    expected_checksum = msg[-5:]
    # step 3: compare with expected checksum
    if calc_checksum == expected_checksum:
        return True
    return False

def start_sender(connection_ID, loss_rate=0, corrupt_rate=0, max_delay=0, transmission_timeout=60):
    """
     This function runs the sender, connnect to the server, and send a file to the receiver.
     The function will print the checksum, number of packet sent/recv/corrupt recv/timeout at the end. 
     The checksum is expected to be the same as the checksum that the receiver prints at the end.

     Input: 
        connection_ID - String
        loss_rate - float (default is 0, the value should be between [0.0, 1.0])
        corrupt_rate - float (default is 0, the value should be between [0.0, 1.0])
        max_delay - int (default is 0, the value should be between [0, 5])
        tranmission_timeout - int (default is 60 seconds and cannot be 0)
     Output: None
    """

    ## STEP 0: PRINT YOUR NAME AND DATE TIME
    name = "Jack Williams"
    print("START receiver - {} @ {}".format(name, datetime.datetime.now()))

    ## STEP 1: CONNECT TO THE SERVER
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # set connection timeout
    clientSocket.settimeout(CONNECTION_TIMEOUT)
    try:
        # connect to the server
        clientSocket.connect((SERVER_IP,SERVER_PORT))
    except socket.error as e:
        # print error and terminate if fail
        print('Connection error: {}'.format(e))
        clientSocket.close()
        sys.exit()
    # disable timeout 
    clientSocket.settimeout(None)
    # request a relay service
    message = "HELLO S {} {} {} {}".format(loss_rate, corrupt_rate, max_delay, connection_ID)
    clientSocket.sendall(message.encode("utf-8"))
    print("sending: {}".format(message))
    # wait for message
    recv_message = clientSocket.recv(1024).decode("utf-8")
    print("received: {}".format(recv_message))
    # check response and keep waiting or terminate if the respond is not OK
    while not recv_message.startswith("OK"):
        if recv_message.startswith("WAITING"):
            # wait
            print("Waiting for a receiver")
            recv_message = clientSocket.recv(1024).decode("utf-8")
            
        elif recv_message.startswith("ERROR"):
            # print error and terminate
            print("Error: {}".format(recv_message.split(' ')[1]))
            exit()
        else:
            # invalid message, print and temrinate
            print("Error: Invalid message from server during connection. The message is {}".format(recv_message))
            exit()

    print("ESTABLISHED A CHANNEL @ {}".format(datetime.datetime.now()))

    ## STEP 2: READ FILE
    # read file
    filename = 'declaration.txt'
    with open(filename, 'r') as f:
        data = f.read()

    # some helpful variables but you don't have to use all of them
    pointer = 0
    SEQ = 0
    ACK = 0
    total_packet_sent = 0
    total_packet_recv = 0
    total_corrupted_pkt_recv = 0
    total_timeout =  0
    payload = ""
    checksumValue = 0
    increment = 20

    # set transmission timeout (set to 3 seconds if input is less or equal to zero)
    if transmission_timeout <= 0:
        transmission_timeout = 3
    clientSocket.settimeout(transmission_timeout)
    
    # send the first 200 characters
    to_send_size = 200

    # STEP 3: SEND FILE                
    state = "wait for ACK 0"
    
    ##################################################
    # START YOUR RDT 3.0 SENDER IMPLEMENTATION BELOW #
    ##################################################

    while(increment <= to_send_size):
        # since we never need to wait for the call from above, we can bypass that state
        if(state == "wait for ACK 0"):

            # create packet
            payload = data[increment - 20:increment]
            packet = "{} {} {} ".format(SEQ, ACK, payload)
            checksumValue = checksum(packet)
            packet = "{}{}".format(packet, checksumValue)
            
            # send packet data
            clientSocket.send(packet.encode("utf-8"))
            total_packet_sent += 1
            
            # set timeout
            clientSocket.settimeout(transmission_timeout)

            # sent packet
            #print("{}: sending: {}".format(datetime.datetime.now(), packet))

            # wait for ACK 0
            while(1):
                try:
                    # received packet
                    recv_message = clientSocket.recv(30).decode("utf-8")

                    # received packet 
                    #print("{}: received: {}".format(datetime.datetime.now(), recv_message))

                    total_packet_recv += 1

                    # check if packet is not corrupted and has been correctly acknowledged
                    if(checksum_verifier(recv_message) and recv_message[2] == '0'):
                        state = "wait for ACK 1"
                        clientSocket.settimeout(None) # stop timer
                        increment += 20
                        SEQ = 1
                        ACK = 1
                        break
                    # check if packet is corrupted or incorrect acknowledgment received
                    elif(not checksum_verifier(recv_message) or recv_message[2] == '1'):
                        total_corrupted_pkt_recv += 1
                        # loop back and wait to receive packet

                except socket.timeout:
                    # stop timer, send new packet, process timout, retry sending packet and restart timer
                    clientSocket.settimeout(None)
                    clientSocket.send(packet.encode())
                    # sent packet
                    #print("{}: sending: {}".format(datetime.datetime.now(), packet))

                    # reset timeout
                    clientSocket.settimeout(transmission_timeout)
                    total_packet_sent += 1
                    total_timeout += 1

        elif(state == "wait for ACK 1"):  
            # create packet
            payload = data[increment - 20:increment]
            packet = "{} {} {} ".format(SEQ, ACK, payload)
            checksumValue = checksum(packet)
            packet = "{}{}".format(packet, checksumValue)

            # send packet data
            clientSocket.send(packet.encode("utf-8"))
            total_packet_sent += 1
            
            # set timeout
            clientSocket.settimeout(transmission_timeout)

            # sent packet
            #print("{}: sending: {}".format(datetime.datetime.now(), packet)) 

            while(1):
                try:
                    # received packet
                    recv_message = clientSocket.recv(30).decode("utf-8")
                    total_packet_recv += 1

                    # received packet 
                    #print("{}: received: {}".format(datetime.datetime.now(), recv_message))

                    # check if packet is not corrupted and has been correctly acknowledged
                    if(checksum_verifier(recv_message) and recv_message[2] == '1'):
                        state = "wait for ACK 0"
                        clientSocket.settimeout(None) # stop timer
                        increment += 20
                        SEQ = 0
                        ACK = 0
                        break
                    # check if packet is corrupted or incorrect acknowledgment received
                    elif(not checksum_verifier(recv_message) or recv_message[2] == '0'):
                        total_corrupted_pkt_recv += 1
                        # loop back and wait to receive packet

                except socket.timeout:
                    # stop timer, send new packet, process timout, retry sending packet and restart timer
                    clientSocket.settimeout(None)
                    clientSocket.send(packet.encode())
                    # sent packet
                    #print("{}: sending: {}".format(datetime.datetime.now(), packet))
                    
                    # reset timeout
                    clientSocket.settimeout(transmission_timeout)
                    total_packet_sent += 1
                    total_timeout += 1
                
    
    ########################################
    # END YOUR RDT 3.0 SENDER IMPLEMENTATION HERE #
    ########################################

    # close the socket
    clientSocket.close() 

    # print out your name, the date and time,
    print("DONE sender - {} @ {}".format(name, datetime.datetime.now()))

    # print checksum of the sent file 
    print("File checksum: {}".format(checksum(data[:to_send_size])))
    # print stats
    print("Total packet sent: {}".format(total_packet_sent))
    print("Total packet recv: {}".format(total_packet_recv))
    print("Total corrupted packet recv: {}".format(total_corrupted_pkt_recv))
    print("Total timeout: {}".format(total_timeout))
 
if __name__ == '__main__':
    # check arguments
    if len(sys.argv) != 6:
        print("Expected \"python PA2_sender.py <connection_id> <loss_rate> <corrupt_rate> <max_delay> <transmission_timeout>\"")
        exit()
    connection_ID, loss_rate, corrupt_rate, max_delay, transmission_timeout = sys.argv[1:]
    # start sender
    start_sender(connection_ID, loss_rate, corrupt_rate, max_delay, float(transmission_timeout))

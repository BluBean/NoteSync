#!/usr/bin/env python3
import os, socket, sys
import sounddevice as sd
import soundfile as sf

###########################################################
#### Teacher Client Connection
#
###########################################################

s = socket.socket()      # Create a socket object
#HOST = '18.220.239.193'  # ec2 server
HOST = '127.0.0.1'       # local host
T_PORT = 60003           # Reserve a port for your service.

### main client program ###
#if len(sys.argv) != 4:
#    print("Syntax: python3 client_test.py <student number> <host> <wav file>")
#    sys.exit(0)

# add check to verify file exists or quit
#if not os.path.exists(file):
#    print(file + " does not exist. Exiting.")
#    sys.exit(0)

#if int(student) > 9 or int(student) < 0:
#    print("Student number is invalid. Valid student numbers are 0-9.")
#    sys.exit(0)


# send GUI data from metronome to server
def send_GUI_data():
    student = '1'
    s.send(str.encode(student))
    print("Sent student info")
    return

def close_conn():
    print("Done Sending")
    s.shutdown(socket.SHUT_WR)
    print(s.recv(1024))
    s.close()

# connect to server
def conn_server():
    s.connect((HOST, T_PORT))
    print("Connected.")

conn_server()
send_GUI_data()
close_conn()


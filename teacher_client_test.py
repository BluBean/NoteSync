#!/usr/bin/env python3
import os, socket, sys
from typing import List
import json
import sounddevice as sd
import soundfile as sf


# Globals
s = socket.socket()      # Create a socket object
#HOST = '18.220.239.193'  # ec2 server
HOST = '127.0.0.1'       # local host
T_PORT = 60003           # Reserve a port for your service.


###########################################################
#### Teacher Client Connection
#
###########################################################

# connect to server
def conn_server():
    s.connect((HOST, T_PORT))
    print("Connected.")


# close connection to server
def close_conn():
    print("Done Sending")
    s.shutdown(socket.SHUT_WR)
    print(s.recv(1024))
    print("Goodbye.")
    s.close()


# send teacher GUI data to server
def send_GUI_data(ids):

    # teacher GUI data
    metronome = pull_metronome()
    offsets = pull_offsets(ids)

    # Send metronome
    s.send(bytes(metronome, 'utf-8'))
    print("Sent metronome info")

    # Send offsets dictionary
    s.send(json.dumps(offsets, indent=2).encode('utf-8') + b"\n")
    print("Sent student offset info")

    return


###########################################################
#### Pull data from teacher client GUI
#    to send to server
#
###########################################################

# pull student offset values; store in a dictionary
def pull_offsets(ids: List) -> dict:
    store = {}
    """
    Pull values from offset table.
    Store in dictionary.

    ids : student IDs

    return as a dictionary to send to server
    """
    for val in ids:
        store[val] = "1"
    return store
    #return '1'


# pull metronome values; store in a string
def pull_metronome() -> str:
    """
    Pull values from metronome.
    Values must be 3 digits each. ex: t_sig = 004

    bpm : bpm
    t_sig : time signature numerator
    tot_measures: total number of measures

    return as a string to send to server
    """

    # test values
    bpm = 123
    t_sig = 456
    tot_measures = 789
    return str(bpm) + "," + str(t_sig) + "," + str(tot_measures)


### main program ###
def teacher_main():
    # available student IDs
    ids = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    # connect and send data to server
    conn_server()
    send_GUI_data(ids)

    # close connection with server
    close_conn()


# run teacher client file
teacher_main()

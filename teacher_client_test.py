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
    print("Goodbye.")
    s.close()


# send teacher GUI data to server
def send_GUI_data(ids):

    # teacher GUI data
    metronome = pull_metronome()
    num_students = pull_num_students()
    offsets = pull_offsets(ids)

    # Send metronome
    s.send(bytes(metronome, 'utf-8'))
    print("Sent metronome info")

    # Send number of students (0-9)
    s.send(bytes(num_students, 'utf-8'))
    print("Sent num_students info")

    # Send offsets dictionary
    s.send(json.dumps(offsets, indent=2).encode('utf-8') + b"\n")
    print("Sent student offset info")

    print(s.recv(1024))

    return


# receive final mix as WAV
def receive_mix():

    # generate empty wav file
    f = open('NoteSync.wav', "w+")
    f.close()

    # Try to receive the WAV
    print("Receiving mixed wav file...")

    # write to corresponding student audio file
    with open(f"NoteSync.wav", "wb") as f:
        data = s.recv(4096)
        while data:
            print(f"Receiving {len(data)} bytes...")
            f.write(data)
            data = s.recv(4096)

    print("Done receiving.")
    s.send(b"sick mixtape G")
    print("close conn at receive_mix.")
    s.close()

###########################################################
#### Pull data from teacher client GUI
#    to send to server
#
###########################################################

# pull metronome values from GUI; store in a string
def pull_metronome() -> str:
    """
    Pull values from metronome.
    Values must be int with length == 3. ex: t_sig = 004

    bpm : bpm
    t_sig : time signature numerator
    tot_measures: total number of measures

    return as a string to send to server
    """
    # test values
    """    bpm = mainwindow.bpm_slider.get()
    t_sig = mainwindow.time_sig_slider.get()
    tot_measures = mainwindow.measures_slider.get()"""
    bpm = 72  # test
    t_sig = 4  # test
    tot_measures = 4  # test
    # bit manipulation
    if bpm < 10:
        bpm = "00"+str(bpm)
    elif bpm < 100:
        bpm = "0"+str(bpm)
    if t_sig <10:
        t_sig = "00" + str(t_sig)
    else:
        t_sig= "0"+str(t_sig)
    if tot_measures <10:
        tot_measures = "00" + str(tot_measures)
    else:
        tot_measures= "0"+str(tot_measures)

    #print(str(bpm) + "," + str(t_sig) + "," + str(tot_measures))

    return str(bpm) + "," + str(t_sig) + "," + str(tot_measures)


# pull num_students value from GUI; store in a string
def pull_num_students() -> str:
    #returns single digit from 0-9

    return str(1)  # test return
    #return str(num_students)


# pull student offset values from GUI; store in a dictionary
def pull_offsets(ids: List) -> dict:
    store = {}
    """
    Pull values from offset table.
    Store offset as string in dictionary (samples or measures)

    ids : student IDs

    return as a dictionary to send to server
    """

    for val in ids:
        #store={"val":mainwindow.s[val].get()}
        store[val] = "1"
    return store


### main program ###
def teacher_main():
    # available student IDs
    ids = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    # connect and send data to server
    conn_server()
    send_GUI_data(ids)

    # wait to receive final wav file
    while True:
        notify = s.recv(4)  # waits for notification from server
        print("received notification: ", notify)
        if notify == b'done':
            break
        elif notify != b'done':
            s.close()
            print("Failed to receive notification")
            exit()

    # try to receive wav
    receive_mix()

    # close connection with server
    #close_conn()

    print('system exit')
    sys.exit(0)


# run teacher client file
teacher_main()

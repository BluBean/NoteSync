#!/usr/bin/env python3

# Imports
import socket
import threading
from _thread import *
from typing import List
import json


# Globals
T_PORT = 60003  # teacher port
S_PORT = 60002  # student port
T_CONNECTIONS = {}
S_CONNECTIONS = {}
T_CONN_LOCK = False
S_CONN_LOCK = False


###########################################################
#### Teacher Connection
#
# receives teacher GUI data
# sends finished wav file
###########################################################

# allow for threading teacher connection
class TeacherThread(threading.Thread):
    def __init__(self, taddr, tconn):
        threading.Thread.__init__(self)
        self.taddr = taddr
        self.tconn = tconn
        print(f"New connection {self.taddr}")


    def run(self):
        global T_CONNECTIONS
        global T_CONN_LOCK
        try:
            t_download_seq(self.tconn, self.taddr)
        except:
            self.tconn.close()
            print("Failed to download from teacher")
            pass
        # Remove from connections list
        while T_CONN_LOCK:
            pass
        T_CONN_LOCK = True
        T_CONNECTIONS.pop(self.taddr)
        T_CONN_LOCK = False


# listen until teacher connects to server
def teacher_serve():
    """
    Start socket server
    """
    global T_CONNECTIONS
    global T_CONN_LOCK

    # create socket for teacher with timeout (sec)
    s = create_socket(T_PORT, 10)

    print('Server listening for teacher....')

    while True:
        s.listen(1)
        # Catch connection
        try:
            conn, addr = s.accept()
            print("Teacher connected.")
        except socket.timeout:  # stop listening after timeout (sec)
            break
        tt = TeacherThread(addr, conn)

        # make sure threads don't mess with each other
        while T_CONN_LOCK:
            pass
        T_CONN_LOCK = True
        T_CONNECTIONS[addr] = conn
        T_CONN_LOCK = False
        tt.start()  # start thread


def t_download_seq(conn, addr):
    global T_CONNECTIONS

    # Try to receive metronome data (bpm, num_measures, tot_measures)
    metronome = conn.recv(11)
    print("metronome: ", metronome)

    # Try to receive and deserialize offsets dictionary
    offsets = json.loads(conn.recv(1024))
    print("offsets: ", offsets)

    print("Done receiving teacher GUI data")
    conn.send(b"We will be with you shortly...")
    conn.close()


###########################################################
#### Student Connections
#
# receives: student GUI data; student recording
# sends: student offset; metronome data
###########################################################

# allow for threading client connections
class ServerThread(threading.Thread):
    def __init__(self, caddr, cconn, offsets, metronome):
        threading.Thread.__init__(self)
        self.caddr = caddr
        self.cconn = cconn
        self.offsets = offsets
        self.metronome = metronome
        print(f"New connection {self.caddr}")


    def run(self):
        global S_CONNECTIONS
        global S_CONN_LOCK
        try:
            s_download_seq(self.cconn, self.caddr, self.offsets, self.metronome)
        except:
            self.cconn.close()
            print("Failed to download from student")
            pass
        # Remove from connections list
        while S_CONN_LOCK:
            pass
        S_CONN_LOCK = True
        S_CONNECTIONS.pop(self.caddr)
        S_CONN_LOCK = False


def create_socket(port, t_sec):
    '''
    Create socket for listening.
    '''
    # Create TCP socket and set options
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.settimeout(t_sec)

    # Grab host addr
    host = socket.gethostname()

    # Bind to port
    #s.bind((host, port))  # ec2 server
    s.bind(("127.0.0.1", port))  # local

    return s


def serve(ids):
    """
    Start socket server
    """
    global S_CONNECTIONS
    global S_CONN_LOCK

    # create socket for student
    s = create_socket(S_PORT, 5)

    print('Server listening....')

    # store offsets from offset calculator to send to client
    offsets = get_offsets(ids)
    # store metronome values from GUI to send to client
    metronome = get_metronome()

    while True:
        s.listen(1)
        # Catch connection
        try:
            conn, addr = s.accept()
        except socket.timeout:  # stop listening after timeout (sec)
            break
        st = ServerThread(addr, conn, offsets, metronome)
        #st = ServerThread(addr, conn, offsets)

        # make sure threads don't mess with each other
        while S_CONN_LOCK:
            pass
        S_CONN_LOCK = True
        S_CONNECTIONS[addr] = conn
        S_CONN_LOCK = False
        st.start()  # start thread

    # keep processing until no connections remain
    while len(S_CONNECTIONS) > 0:
        pass


def s_download_seq(conn, addr, offsets, metronome):
    global S_CONNECTIONS
    # Decide the student number
    sid = int(conn.recv(1).decode())

    # Send metronome
    conn.send(bytes(metronome, 'utf-8'))
    # Send back offset
    conn.send(bytes(offsets[sid], 'utf-8'))

    # Try to receive the WAV
    print("Receiving student wav file...")

    # write to corresponding student audio file
    with open(f"student_{sid}.wav", "wb") as f:
        data = conn.recv(4096)
        while data:
            print(f"Receiving {len(data)} bytes...")
            f.write(data)
            data = conn.recv(4096)

    print("Done receiving.")
    conn.send(b"Thank you for connecting. Please come again!")
    conn.close()


###########################################################
#### GUI and calculations
#
###########################################################

# use values retrieved from server GUI to calculate offset
def wav_file_calculation(bpm: int, num_measures: int, tot_measures: int) -> int:
    '''
    bpm : bpm
    num_measures: number of measures for offset to be
    tot_measures: total number of measures

    returns: number of samples gets returned as a string
    '''
    value = "0"
    return value


# retrieve metronome values from GUI for use in calculations
def pull_values():
    """
    Pull values from metronome.

    bpm : bpm
    time_sig : time signature numerator
    tot_measures: total number of measures
    """
    return 0, 0, 0


# store calculated offsets in dictionary
def get_offsets(ids: List) -> dict:
    store = {}
    bpm, num_measures, tot_measures = pull_values()
    for val in ids:
        store[val] = wav_file_calculation(bpm, num_measures, tot_measures)
    return store


# store metronome values in string
def get_metronome() -> str:
    bpm, num_measures, tot_measures = pull_values()
    return str(bpm) + "," + str(num_measures) + "," + str(tot_measures)


### main program ###
teacher_serve()
#serve([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])

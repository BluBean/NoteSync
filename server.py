#!/usr/bin/env python3

# Imports
import socket
import threading
from _thread import *
from typing import List

# Globals
PORT = 60002
CONNECTIONS = {}
CONN_LOCK = False


# allow for threading client connections
class ServerThread(threading.Thread):
    def __init__(self, caddr, cconn, offsets):
        threading.Thread.__init__(self)
        self.caddr = caddr
        self.cconn = cconn
        self.offsets = offsets
        print(f"New connection {self.caddr}")

    def run(self):
        global CONNECTIONS
        global CONN_LOCK
        try:
            download_seq(self.cconn, self.caddr, self.offsets)
        except:
            self.cconn.close()
            print("Failed to download from student")
            pass
        # Remove from connections list
        while CONN_LOCK:
            pass
        CONN_LOCK = True
        CONNECTIONS.pop(self.caddr)
        CONN_LOCK = False


def create_socket():
    '''
    Create socket for listening.
    '''
    # Create TCP socket and set options
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.settimeout(20)

    # Grab host addr
    host = socket.gethostname()

    # Bind to port
    s.bind((host, PORT))
    #s.bind(("127.0.0.1", PORT))  # local

    return s


# use values retrieved from server GUI to calculate offset
def wav_file_calculation(bpm: int, num_measures: int, tot_measures: int) -> int:
    '''
    bpm : bpm
    num_measures: number of measures for offset to be
    tot_measures: total number of measures

    returns: number of samples gets returned
    '''
    value = "0"
    return value


# retrieve metronome values from GUI for use in calculations
def pull_values():
    """
    Pull values from metronome.
    """
    return 0, 0, 0


# store calculated offsets in dictionary
def get_offsets(ids: List) -> dict:
    store = {}
    bpm, num_measures, tot_measures = pull_values()
    for val in ids:
        store[val] = wav_file_calculation(bpm, num_measures, tot_measures)
    return store


def download_seq(conn, addr, offsets):
    global CONNECTIONS
    # Decide the student number
    sid = int(conn.recv(1).decode())

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

    print("Done receiving the bacon")
    conn.send(b"Thank you for connecting. Please come again!")
    conn.close()


def serve(ids):
    """
    Start socket server
    """
    global CONNECTIONS
    global CONN_LOCK

    s = create_socket()

    print('Server listening....')

    # store offsets from offset calculator to send to client
    offsets = get_offsets(ids)

    while True:
        s.listen(1)
        # Catch connection
        try:
            conn, addr = s.accept()
        except socket.timeout:  # stop listening after timeout (sec)
            break
        st = ServerThread(addr, conn, offsets)

        # make sure threads don't mess with each other
        while CONN_LOCK:
            pass
        CONN_LOCK = True
        CONNECTIONS[addr] = conn
        CONN_LOCK = False
        st.start()  # start thread

    # keep processing until no connections remain
    while len(CONNECTIONS) > 0:
        pass


serve([1, 3, 4, 5])
# do other things

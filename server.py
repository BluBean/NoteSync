#!/usr/bin/env python3

# Imports
import socket
import threading
import json
import os
import os.path
import time
from pydub import AudioSegment
import soundfile as sf

# double check line 38 when switching between local and ec2


# Globals
T_PORT = 60003  # teacher port
S_PORT = 60002  # student port
T_CONNECTIONS = {}
S_CONNECTIONS = {}
T_CONN_LOCK = False
S_CONN_LOCK = False
T_METRONOME = b''
T_NUM_STUDENTS = b''
T_OFFSETS = {}


def create_socket(port, t_sec, t_type):
    '''
    Create socket for listening.
    '''
    # Create TCP socket and set options
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if t_type == 's':
        s.settimeout(t_sec)

    # Grab host addr
    host = socket.gethostname()

    # Bind to port
    #s.bind((host, port))  # ec2 server
    s.bind(("127.0.0.1", port))  # local

    return s


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
            t_upload_seq(self.tconn, self.taddr)
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


# main program
def main():
    """
    Start socket server
    """
    global T_CONNECTIONS, S_CONNECTIONS
    global T_CONN_LOCK

    # create socket for teacher with timeout (sec)
    s = create_socket(T_PORT, 10, 't')

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

        # wait to receive global parameter updates from teacher
        while (T_METRONOME == b'' or T_NUM_STUDENTS == b'' or T_OFFSETS == {}):
            pass
        print("Updated global variables")

        # start student threads
        serve()
        print("finished student serve.")

        # wait until no student connections remain
        while len(S_CONNECTIONS) > 0:
            pass

        sync_files()  # mixer module

        # send file back to teacher
        print("sending file to teacher")
        t_download_seq(conn, addr)


        ################################
        #   close teacher connections  #
        ################################


        reset_globals()

        exit()


# receive metronome and offset data from teacher client
def t_upload_seq(conn, addr):
    global T_CONNECTIONS, T_METRONOME, T_OFFSETS, T_NUM_STUDENTS

    # Try to receive metronome data (bpm, num_measures, tot_measures)
    metronome = conn.recv(11)
    print("debug_metronome: ", metronome)
    T_METRONOME = metronome.decode('utf-8').split(',')

    # Try to receive number of students (0-9)
    num_students = conn.recv(1)
    print("debug_num_students: ", num_students)
    T_NUM_STUDENTS = num_students.decode('utf-8')

    # Try to receive and deserialize offsets dictionary
    offsets = json.loads(conn.recv(1024))
    print("debug_offsets: ", offsets)
    T_OFFSETS = offsets

    print("Done receiving teacher GUI data")
    conn.send(b"We will be with you shortly...")


# send final mixed wav file to teacher
def t_download_seq(conn, addr):
    global T_CONNECTIONS, T_METRONOME, T_OFFSETS

    # notify teacher client that final wav is ready
    notify = 'done'
    conn.send(bytes(notify, 'utf-8'))
    print("notify: ", notify)

    ### test ###
    # generate empty wav file
    f = open('final_mix.wav', "w+")
    f.close()

    # send the recorded file back to client
    with open('final_mix.wav', 'rb') as f:
        print("Sending...")
        l = f.read(4096)
        while (l):
            print("Sending...")
            conn.send(l)
            l = f.read(4096)

    print("Done Sending")
    conn.shutdown(socket.SHUT_WR)
    print(conn.recv(1024))
    print("t_download_seq complete.")

    conn.close()


def decode_metronome(metronome) -> int:
    # split into variables
    bpm, t_sig, tot_measures = metronome
    bpm = int(bpm)
    t_sig = int(t_sig)
    tot_measures = int(tot_measures)
    #print('bpm:', bpm, ' t_sig:', t_sig, ' tot_measures:', tot_measures)
    return bpm, t_sig, tot_measures


def reset_globals():
    global T_CONNECTIONS, S_CONNECTIONS
    global T_CONN_LOCK, S_CONN_LOCK
    global T_METRONOME, T_OFFSETS

    T_CONNECTIONS = {}
    S_CONNECTIONS = {}
    T_CONN_LOCK = False
    S_CONN_LOCK = False
    T_METRONOME = b''
    T_OFFSETS = {}


###########################################################
#### Student Connections
#
# receives: student GUI data; student recording
# sends: student offset; metronome data
###########################################################

# allow for threading client connections
class StudentThread(threading.Thread):
    def __init__(self, caddr, cconn, metronome, offsets):
        threading.Thread.__init__(self)
        self.caddr = caddr
        self.cconn = cconn
        self.metronome = metronome
        self.offsets = offsets
        print(f"New connection {self.caddr}")


    def run(self):
        global S_CONNECTIONS
        global S_CONN_LOCK
        try:
            s_download_seq(self.cconn, self.caddr, self.metronome, self.offsets)
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


def serve():
    """
    Start socket server
    """
    global S_CONNECTIONS, S_CONN_LOCK
    global T_METRONOME, T_OFFSETS

    # create socket for student
    s = create_socket(S_PORT, 20, 's')

    print('Server listening....')

    # store metronome string to send to client
    metronome = encode_metronome(T_METRONOME)
    print("metronome_serve: ", metronome)

    # store offsets in dictionary to send to client
    offsets = T_OFFSETS
    offsets = {int(k): str(v) for k, v in offsets.items()}
    print("offsets_serve: ", offsets)

    while True:
        s.listen(1)
        # Catch connection
        try:
            conn, addr = s.accept()
        except socket.timeout:  # stop listening after timeout (sec)
            break
        st = StudentThread(addr, conn, metronome, offsets)

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


def s_download_seq(conn, addr, metronome, offsets):
    global S_CONNECTIONS
    # Decide the student number
    sid = int(conn.recv(1).decode())

    # Send metronome
    conn.send(bytes(metronome, 'utf-8'))
    print('metronome download: ', bytes(metronome, 'utf-8'))
    # Send back offset
    conn.send(bytes(offsets[sid], 'utf-8'))
    print('offsets download: ', bytes(offsets[sid], 'utf-8'))

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


# store metronome values in string
def encode_metronome(metronome) -> str:
    bpm, t_sig, tot_measures = metronome
    return str(bpm) + "," + str(t_sig) + "," + str(tot_measures)


###########################################################
#### Calculations
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
    value = "1"
    return value



#################################################################
# Mixer Module
# Calculates offset required
#
# --- inputs:
# beats = beats per measure (from selected time signature)
# num_meas = number of measures from song start
#                     to when student begins
# bpm = beats per minute (tempo)
#rec_length = beats.get() * (num_meas.get() / bpm.get()) #length in seconds
#samples = 48000 * 60 * rec_length  #length to record based on GUI (samples)
#offset_size = 48000 * 60 * (beats.get()/bpm.get())  # samples per measure or known as the amount of samples in an offset
# --- output:
# duration = milliseconds of buffer required
#################################################################
def calc_duration(bpm, beats, num_meas):
    duration = beats * (num_meas / bpm)
    print('duration: ', duration)
    return duration

    """      def read_audio(audio_file):
    rate, data = sf.read(audio_file)  # Return the sample rate (in samples/sec) and data from a WAV file
    return data, rate"""



def sync_files():
    global T_NUM_STUDENTS
    num_students = T_NUM_STUDENTS

    # check_student_files(num_students)
    s_check_received(num_students)

    # print(s1, fs1, s2, fs2)
    data = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    samplerate = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    data = [None] * len(data)
    samplerate = [None] * len(samplerate)
    length = []
    main_file = AudioSegment.from_file("mixer0.wav", format="wav")

    if num_students != 1:
        for id in range(1, num_students):
            strid = str(id)
            dat, samplerat = sf.read("mixer" + strid + ".wav")
            data[id] = dat
            samplerate[id] = samplerat
            info = sf.info('mixer' + strid + '.wav')
            print('\n', info)
            addition_file = AudioSegment.from_file("mixer" + strid + ".wav", format="wav")
            main_file = main_file.overlay(addition_file, position=0)  # Overlay audio2 over audio1
    file_handle = main_file.export("buffered_overlay.wav", format="wav")
    #audio1 = AudioSegment.from_file("audio2.wav", format="wav")
    #audio2 = AudioSegment.from_file("buffered_audio.wav", format="wav")
    #boost1 = audio1 + 9  # audio1 x dB louder (clipping)
    #overlay = boost1.overlay(audio2, position=0)  # Overlay audio2 over audio1
      # export overlaid wav files
    #for id in range(num_itterations):
        #length[id] = len(samplerate[id]) # total number of samples
        #length[id+1] = len(samplerate[id+1])
        #print(length[id],length[id+1])
        #max_samples = max(length[id],length[id+1])  # file with greatest number of samples
        #min_samples = min(length[id],length[id+1])
        #samples_offset = abs(max_samples - min_samples)
        #print(samples_offset)
    # e = s1-s2 # difference signal
    #l1 = len(s1)  # total number of samples
    #l2 = len(s2)
    #print(l1, l2)
    #max_samples = max(l1, l2)  # file with greatest number of samples
    #min_samples = min(l1, l2)
    #samples_offset = abs(max_samples - min_samples)
    #print(samples_offset)

    # add buffer to beginning of shorter audio file
    #buffer = np.zeros(samples_offset)  # generate buffer
    # print(buffer)

    #sf.write('buffer.wav', buffer, 48000)  # create buffer .wav file
    #audio = AudioSegment.from_file('audio1.wav', format="wav")  # open both .wav files to write
    #buffer_audio = AudioSegment.from_file('buffer.wav', format="wav")
    #combined = buffer_audio + audio  # audio with buffer appended at beginning
    #file_handle = combined.export("buffered_audio.wav", format="wav")  # export buffered wav file"""


############################################
##Checking to see if we got all the files
############################################

# Check to see if we got all the files
def s_check_received(num_students):
    files_received = 0  # initialize
    for stu_id in range(0, 10):
        stu_id_str = str(stu_id)
        filename = 'student_' + stu_id_str + '.wav'
        while not os.path.exists(filename):
            pass
        mix_rename = str(files_received)
        os.rename(filename, "mixer" + mix_rename + ".wav")
        files_received = files_received + 1


### main program ###
main()

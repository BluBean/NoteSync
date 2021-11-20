#!/usr/bin/env python3
import os, socket, sys
import sounddevice as sd
import soundfile as sf


# Globals
s = socket.socket() # Create a socket object
student = sys.argv[1]
host = sys.argv[2]
file = sys.argv[3]
S_PORT = 60002 # Reserve a port for your service.


##########################################################
#### Student Client Connection
#
# terminal command (python3 <file> <student#> <AWS ip> <audio#.wav file>)
# python3 student_client_test.py 1 18.220.239.193 audio1.wav  # ec2 server
# python3 student_client_test.py 1 127.0.0.1 audio1.wav  # local host
###########################################################

# check for user input errors
def verify_inputs():
    if len(sys.argv) != 4:
        print("Syntax: python3 client_test.py <student number> <host> <wav file>")
        sys.exit(0)

    # add check to verify file exists or quit
    if not os.path.exists(file):
        print(file + " does not exist. Exiting.")
        sys.exit(0)

    if int(student) > 9 or int(student) < 0:
        print("Student number is invalid. Valid student numbers are 0-9.")
        sys.exit(0)


# main student client code
def stu_main():

    # check for user input errors
    verify_inputs()

    # send the recorded file back to server
    with open (file,'rb') as f:
        # Send student number, get offset
        s.connect((host, S_PORT))
        s.send(str.encode(student))
        print("Sending student ID", student)
        print(str.encode(student))

        # get and store metronome values in a list (bpm, num_measures, tot_measures)
        metronome = s.recv(11)
        print(metronome)

        bpm, t_sig, tot_measures = metronome.split(b',')
        print('bpm: ', bpm, 't_sig: ', t_sig, 'tot_measures: ', tot_measures)


        # get and store offset value for student (samples)
        offset = s.recv(1024)
        print(offset)

        # record and save recording
        record(bpm, t_sig,tot_measures, offset, student)  # (<duration of recording>, <offset>) (samples)

        print("Sending...")
        l = f.read(4096)
        while (l):
            print("Sending...")
            s.send(l)
            l = f.read(4096)
    print("Done Sending")
    s.shutdown(socket.SHUT_WR)
    print(s.recv(1024))
    print("Goodnight, sweet prince.")
    s.close()


"""
# keep trying to connect until connected to server
connected = False
while not connected:
    try:
        s.connect((host, S_PORT))
        connected = True
    except Exception as e:
        pass #Do nothing, just try again
"""


###########################################################
#### Voice recorder MODULE
#
# --- inputs ---
# rec_samples = duration of recording (samples)
# offset = buffer duration (samples)
#
# --- output ---
# write to .wav file
###########################################################


def record(bpm, t_sig,tot_measures, offset, student):
    bpm = int(bpm)
    t_sig = int(t_sig)
    tot_measures = int(tot_measures)
    print('bpm: ', bpm, 't_sig: ', t_sig, 'tot_measures: ', tot_measures)
    # calculate recording length from GUI
    duration = t_sig * 60 * (tot_measures / bpm)  # length (unit: seconds)
    samples = 48000 * duration  # length to record based on GUI (unit: samples)
    offset_size = 48000 * 60 * (t_sig / bpm)  # samples per measure or known as the amount of samples in an offset
    fs = 48000  # Sample rate
    print('offset (samples): ', offset)
    # sd.rec(<length of recording in samples>, <samplerate>, <channels>)
    myrecording = sd.rec(int(duration), samplerate=fs, channels=2)
    sd.wait()  # Wait until recording is finished
    # write('input1.wav', fs, myrecording)  # Save as WAV file
    sf.write('audio' + student + '.wav', myrecording, fs, subtype='PCM_16')
    print('voice recording saved')
##########################################################
#### Metronome
#
###########################################################


### main program ###
stu_main()

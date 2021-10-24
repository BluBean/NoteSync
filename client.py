#!/usr/bin/env python3
import os, socket, sys
import sounddevice as sd
import soundfile as sf

s = socket.socket() # Create a socket object
student = sys.argv[1]
host = sys.argv[2]
file = sys.argv[3]
port = 60001 # Reserve a port for your service.

###########################################################
#### Voice recorder MODULE
###########################################################
class voicerecorder:
    def record(rec_samples, offset):
        fs = 48000  # Sample rate
        duration = rec_samples  # Duration of recording (samples)
        print('offset (samples): ', offset)
        # sd.rec(<length of recording in samples>, <samplerate>, <channels>)
        myrecording = sd.rec(int(duration), samplerate=fs, channels=2)
        sd.wait()  # Wait until recording is finished
        # write('input1.wav', fs, myrecording)  # Save as WAV file
        sf.write('audio1.wav', myrecording, fs, subtype='PCM_16')
        print('voice recording saved')




if len(sys.argv) != 4:
    print("Syntax: python3 client.py <student number> <host> <wav file>")
    sys.exit(0)

# add check to verify file exists or quit
if not os.path.exists(file):
    print(file + " does not exist. Exiting.")
    sys.exit(0)

if int(student) > 9 or int(student) < 0:
    print("Student number is invalid. Valid student numbers are 0-9.")
    sys.exit(0)


# send the recorded file back to server
with open (file,'rb') as f:
    # Send student number, get offset
    s.connect((host, port))
    s.send(str.encode(student))
    offset = s.recv(1024)  # get and store offset value for student (samples)
    print(offset)
    # record and save recording
    voicerecorder.record(96000, offset)  # (<duration of recording>, <offset>) (samples)

    print("Sending...")
    l = f.read(4096)
    while (l):
        print("Sending...")
        s.send(l)
        l = f.read(4096)
print("Done Sending")
s.shutdown(socket.SHUT_WR)
print(s.recv(1024))
s.close()

"""
# keep trying to connect until connected to server
connected = False
while not connected:
    try:
        s.connect((host,port))
        connected = True
    except Exception as e:
        pass #Do nothing, just try again
"""

### terminal command (python3 <file> <student#> <AWS ip> <audioX.wav file>)
# python3 client.py 1 100.26.31.241 audio1.wav

#!/usr/bin/env python3

import socket, os, sys, time
port = 60001                  # Reserve a port for your service.
s = socket.socket()             # Create a socket object
host = socket.gethostname()

# Get local machine name
s.bind((host, port))
# Bind to the port
s.listen()                     # Now wait for client connection.

print('Server listening....')
is_finished_recording = False

# main function
def start_process():
    send_data(calc_offsets())  # get all data inputted by teacher, then send data to get_audio()

def calc_offsets():
    # Get all data that teacher inputted, send data to getAudio
    #        Stu  offset
    # Student 0   : 16
    # Student 1  :  2
    return {"0":"16","1":"2", "2":"6"}  # student_num : offset value

# Gives offset values to client
def send_data(offsets):
    conn, addr = s.accept()  # Establish connection with client.
    print('Got connection from', addr)
    print("Receiving student number...")
    first_byte = conn.recv(1)
    decoded = first_byte.decode()
    if int(decoded) == 0:
        conn.send(bytes(offsets["0"], 'utf-8'))  # offset for student 0
    elif int(decoded) == 1:
        conn.send(bytes(offsets["1"], 'utf-8'))  # offset for student 1
    elif int(decoded) == 2:
        conn.send(bytes(offsets["2"], 'utf-8'))  # offset for student 2
    elif int(decoded) == 3:
        conn.send(bytes(offsets["3"], 'utf-8'))  # offset for student 3
    elif int(decoded) == 4:
        conn.send(bytes(offsets["4"], 'utf-8'))  # offset for student 4
    elif int(decoded) == 5:
        conn.send(bytes(offsets["5"], 'utf-8'))  # offset for student 5
    elif int(decoded) == 6:
        conn.send(bytes(offsets["6"], 'utf-8'))  # offset for student 6
    elif int(decoded) == 7:
        conn.send(bytes(offsets["7"], 'utf-8'))  # offset for student 7
    elif int(decoded) == 8:
        conn.send(bytes(offsets["8"], 'utf-8'))  # offset for student 8
    elif int(decoded) == 9:
        conn.send(bytes(offsets["9"], 'utf-8'))  # offset for student 9
    #print("Offset sent to student")

    # wait for student to record and send audio file
    print("wait start")
    time.sleep(5)  # pause code for 5 seconds
    print("wait stop")

    ##  after student is done recording, receive audio file from student
    print("Receiving student wav file...")
    f = open('student' + decoded + '.wav', 'wb')
    l = conn.recv(4096)
    while (l):
        print("Receiving...")
        f.write(l)
        l = conn.recv(4096)
    f.close()
    print('Done receiving')
    conn.send(b'Thank you for connecting')
    conn.close()

# run server.py
while True:
    start_process()

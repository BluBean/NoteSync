#!/usr/bin/env python3

import socket, threading, os, sys, time

PORT = 60001                  # Reserve a port for your service.
s = socket.socket()             # Create a socket object
HOST = socket.gethostname()

# Get local machine name
s.bind((HOST, PORT))
# Bind to the port
s.listen(1)                     # Now wait for client connection.

print('Server listening....')

while True:
    conn, addr = s.accept()     # Establish connection with client.
    print('Got connection from', addr)
    print("Receiving...")
    first_byte = conn.recv(1)
    decoded = first_byte.decode()
    f = open('student' + decoded + '.wav', 'wb')
    l = conn.recv(4096)
    while (l):
       print("Receiving...")
       f.write(l)
       l = conn.recv(4096)
    f.close()
    print('Done receiving')
    conn.send(b'Thank you for connecting')

    #### if else offset calc needs to be before f = open()...
    if int(decoded) == 2:
        conn.send(b'2') # offset
    else:
        conn.send(b'3') # offset for another student
    ####

    conn.close()

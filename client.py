#!/usr/bin/env python3
import os, socket, sys

s = socket.socket() # Create a socket object
student = sys.argv[1]
host = sys.argv[2]
file = sys.argv[3]
port = 60001 # Reserve a port for your service.

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

with open (file,'rb') as f:
    s.connect((host, port))
    print("Sending...")
    l = f.read(4096)
    s.send(str.encode(student))
    while (l):
        print("Sending...")
        s.send(l)
        l = f.read(4096)
print("Done Sending")
s.shutdown(socket.SHUT_WR)
print(s.recv(1024))
print(b"Offset is : " + s.recv(1024))

# recording start

# recording stop

# send the file that was recorded to the server
s.close()

### terminal command (python3 <file> <student#> <AWS ip> <audioX.wav file>)
# python3 client.py 1 100.26.31.241 audio1.wav


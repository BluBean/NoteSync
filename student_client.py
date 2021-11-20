import os, socket, sys


import sounddevice as sd
import soundfile as sf
from inspect import signature

#imports for GUI module
from tkinter import *
from tkinter import filedialog
from functools import partial
from PIL import ImageTk as itk, Image
import threading
from playsound import playsound
import os
import sys
import sounddevice as sd
from scipy.io.wavfile import write
###################################
###Imports for DSP module
import numpy as np
from pydub import AudioSegment
import soundfile as sf
from sys import argv
## Import for metronome
import time




##########################################################
#### Student Client Connection
#
###########################################################

def main(student, host, file):
    sig = signature(main)
    params = sig.parameters
    s = socket.socket()  # Create a socket object
    # student = sys.argv[1]
    # host = sys.argv[2]
    # file = sys.argv[3]
    S_PORT = 60002  # Reserve a port for your service.




    ### main client program ###
    if len(params) != 3:
        print("Syntax: python3 TestClient.py <student number> <host> <wav file>")
        sys.exit(0)
   # print ('checkpoint 1')
    # add check to verify file exists or quit
    if not os.path.exists(file):
        print(file + " does not exist. Exiting.")
        sys.exit(0)
    #print('checkpoint 2')
   #if int(student) > 9 or int(student) < 0:
   #     print("Student number is invalid. Valid student numbers are 0-9.")
   #     sys.exit(0)

    # send the recorded file back to server
    with open(file, 'rb') as f:
        # Send student number, get offset
        s.connect((host, S_PORT))
        s.send(str.encode(student))
        print("Sending student ID", student)
        print(str.encode(student))

        offset = s.recv(1024)  # get and store offset value for student (samples)
        #print(offset)
        metronome = s.recv(1024)  # get and store metronome values in a list (bpm, num_measures, tot_measures)
        print(metronome)
        bpm, t_sig, tot_measures = metronome.split(b',')
        print('bpm: ', bpm, 'time_sig: ', t_sig, 'tot_measures: ', tot_measures)
        #deconstruct values
        bpm = int(bpm)
        t_sig = int(t_sig)
        tot_measures = int(tot_measures)
        print('bpm: ', bpm, 't_sig: ', t_sig, 'tot_measures: ', tot_measures)

        #calculate recording length from GUI
        rec_length = t_sig *60* (tot_measures / bpm)  # length (unit: seconds)
        samples = 48000 * rec_length  # length to record based on GUI (unit: samples)
        offset_size_sec =60 * (t_sig/ bpm) #time per measure in seconds, so seconds per measure
        offset_size = 48000 * 60 * (t_sig/ bpm)  # samples per measure or known as the amount of samples in an offset

        # record and save recording
        backgroundmetro(metronome, bpm, t_sig)
        record(samples,offset_size_sec, offset,student)  # (<duration of recording>,<offset_size>, <offset>, <student#>) (samples)

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
            s.connect((host, S_PORT))
            connected = True
        except Exception as e:
            pass #Do nothing, just try again
    """

    ### terminal command (python3 <file> <student#> <AWS ip> <audio#.wav file>)
    # python3 client.py 1 18.220.239.193 audio1.wav


"""if __name__=='__main__':
    sys.exit(main(sys.argv[1], sys.argv[2]))"""


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
def record(rec_samples,offset_size, offset, student):
    delay_display = (offset_size * offset)
    threading.timer(delay_display,mainwindow.metro_display.configure(bg='red') ).start()
    # print('checkpoint recorder')
    #mainwindow.metro_display.configure(bg='red')
    fs = 48000  # Sample rate
    duration = rec_samples  # Duration of recording (samples)
    print('offset (samples): ', offset)
    # sd.rec(<length of recording in samples>, <samplerate>, <channels>)
    myrecording = sd.rec(int(duration), samplerate=fs, channels=2)
    sd.wait()  # Wait until recording is finished
    # write('input1.wav', fs, myrecording)  # Save as WAV file
    sf.write('audio' + student + '.wav', myrecording, fs, subtype='PCM_16')
    print('voice recording saved')
    mainwindow.metro_display.configure(bg='blue')

###########################################################
#### Client MODULE
###########################################################
###########################################################
#### Various functions
###########################################################

#############################
# Metronome module
#############################
  # Collect beats per minute and time signature from user
  #  bpm = int(input("Enter bpm value: "))
  #  tsig = int(input("Enter bpb value: "))

    # define metronome tool
def metronome(bpm, tsig):
    global gnomestatus
    global metrostatus
    sleep = 60.0 / bpm
    counter = 0
    metrovalue = 0
    while gnomestatus: # =True:
        counter += 1
        if counter % tsig:
            print(f'tock')
            playsound('tock.wav', False)
            metrovalue=metrovalue+1
            metrostatus.set(metrovalue)
        else:
            print(f'TICK')
            playsound('Tick.wav', False)
            metrovalue = tsig
            metrostatus.set(metrovalue)
            time.sleep(sleep)
            mainwindow.after(1,start_stop(bpm, tsig))

        time.sleep(sleep)

def background(func, arg1, arg2):
    t = threading.Thread(target=func, args= (arg1, arg2))
    t.start()

def backgroundmetro(func, bpm, tsig):
    global metrostatus
    metrovalue = 0
    sleep = 60.0 / bpm
    counter = 0
    counter += 1
    if counter % tsig:
        print(f'tock')
        playsound('tock.wav', False)
        metrovalue = metrovalue + 1
        metrostatus.set(metrovalue)
    else:
        print(f'TICK')
        playsound('Tick.wav', False)
        metrovalue = tsig
        metrostatus.set(metrovalue)
        time.sleep(sleep)
    background(func, bpm, tsig)

    # run metronome tool with given values
    #metronome(bpm, tsig)
#############################
#Gui module
#############################

def initialpopup():
    Initialpopup = Tk()
    Initialpopup.title("Welcome to NoteSync")
    Initialpopup.iconbitmap("NoteSync_icon.ico")
    Initialpopup.config(background='#5865F2')
    logo = PhotoImage(file="NoteSync_logo_purp.png")
    label1 = Label(Initialpopup, image= logo, bg = "#5865F2")
    label1.pack()
    label2 = Label(Initialpopup, text ="Audio Synchronization Tool for Remote Learning", bg = "#5865F2")
    label2.pack()
    #button1 = Button(Initialpopup, text="Get Started!", command = startrecording)
    button1 = Button(Initialpopup, text="Get Started!",command=Initialpopup.destroy, bg = "#F6F6F6")
    button1.pack()
    #button2 = Button(Initialpopup, text="Stop Recording", command = stoprecording)
    #button2.pack()
    Initialpopup.mainloop()

def authors():
    authors_name = Tk()
    authors_name.title("Authors")
    authors_name.iconbitmap("NoteSync_icon.ico")
    authors_name.geometry("700x100")
    authors_name.config(background='#5865F2')
    authors_label = Label(authors_name, text ="Notesync created by: Alec Dorn, Brandon Buccola, David Pivonka, Lance McKay, and Michael Moreno", bg = "#5865F2")
    authors_label.pack()
    mentor_label = Label(authors_name, text ="Program Mentor: Shamala Chickamenahalli", bg = "#5865F2")
    mentor_label.pack()
    authors = Button(authors_name, text="OK", command=authors_name.destroy, bg = "#FFFFFF")
    authors.pack()
    authors_name.mainloop()

def help():
    tutorial = Tk()
    tutorial.title("Notesync User Guide")
    tutorial.iconbitmap("NoteSync_icon.ico")
    tutorial.geometry("700x300")
    #gotit = Button(tutorial, text="Thanks for the help!", command=tutorial.destroy)
    text_widget = Text(tutorial) #, height=400, width=40
    #scroll_bar = Scrollbar(tutorial)

    #scroll_bar.pack(side=RIGHT, fill="y", expand=False)
    text_widget.pack(side=LEFT, fill="both", expand=True)
    #text_widget.config(yscrollcommand=scroll_bar.set)
    long_text = """Please follow these steps to successfully operate NoteSync:
    
            1.You will be provided a student number by the teacher.
            You will need to enter it in the "Student Number Select"
            section.
            
            2.Wait until the teacher instructs you to press "Run Client"
            
            3.You will see an indicator that shows you when you can sing.
            the indicator will be red for the countdown and then it will 
            turn blue when the program is recording and you wil hear a
            metronome that is controlled by the teacher.
            
            4.All set! At the end of the recording, your audio file will 
            be sent to the teacher so that it can be combined with the 
            other singer's audio.
            
            Thank you for choosing NoteSync!!!!!!!!!
    """
    text_widget.insert(END, long_text)
    text_widget.configure(state='disabled')
    #gotit.pack(side=BOTTOM)

#menu commands
def new_command():
    file_path0 = filedialog.askopenfilename()
def save_command():
    file_path = filedialog.asksaveasfilename()
    file_selected = 1
# command to run Client
def runClient(student ,ipadd):
    #os.system('TestClient.py 2 18.220.239.193 audio2.wav')
    print(ipadd)
    stu = student.get()
    filename = 'audio' + stu + '.wav'
    f = open(filename, "w+")
    f.close()

    main(stu, ipadd, filename)

def start_stop(bpm, beats):
    global gnomestatus
    if mainwindow.var.get()== 1:
        gnomestatus = True
        metronome(bpm, beats)
    else:
        gnomestatus = False
        metronome(bpm, beats)
#button to start other modules
def recorderlaunch(bpm, t_sig, tot_meas):
    print('Recording in progress')
    rec_length = t_sig * (tot_meas / bpm) #length in seconds
    samples = 48000 * 60 * rec_length  #length to record based on GUI (samples)
    offset_size = 48000 * 60 * (t_sig/bpm)  # samples per measure or known as the amount of samples in an offset
    main.record(samples, offset_size)  # args  record(<samples in recording>, <samples in offset>)

def mainwindow():
    mainwindow = Tk()
    mainwindow.title("NoteSync")
    mainwindow.iconbitmap("NoteSync_icon.ico")
    mainwindow.geometry("300x200")
    main_menu = Menu(mainwindow)
    mainwindow.config(background='#5865F2')
    mainwindow.config(menu=main_menu)



    #create new menu options

    file_menu = Menu(main_menu)
    # Dropdown menu at the top of GUI
    main_menu.add_cascade(label="Options",menu=file_menu)
    #file_menu.add_command(label="New...", command=new_command)
    #file_menu.add_command(label="Save Location", command=save_command)
    file_menu.add_command(label="Help", command=help)
    file_menu.add_command(label="Authors", command=authors)
    file_menu.add_command(label="Exit", command=mainwindow.quit)

    # Button to activate 'TestClient.py'
    #student = '2'
    #ipadd = '18.220.239.193'
    ipadd= '127.0.0.1'
    #filename = 'audio2.wav'
    current_value = '0'
    student_label = Label(mainwindow, text ="Student number select", font=("32"), bg = "#5865F2")
    student_spin = Spinbox(mainwindow, from_ = 0, to = 9, wrap = True,width = 2, font=("Arial 32"), bg = "#5865F2")

    Clybutton = Button(mainwindow, text="Run Client",font=("32"), command= partial( background,runClient,student_spin ,ipadd),bg = "#F6F6F6")
    global metrostatus
    metrostatus = IntVar()

    metro_display = Label(mainwindow, width=2, font=("Arial", 45),bg="#5865F2", textvariable=metrostatus) #, font=("Arial 32 bold"), bd = 0, fg = 'red')

    #metrostatus.set(0)

    #metro_display.configure(state='disabled')

    var = IntVar()
    bpm = 100
    time_sig = 8
    play = Checkbutton(mainwindow,variable=var, command=partial(backgroundmetro,start_stop, bpm,time_sig))
    #play.pack() #uncomment this line to test metronome

    student_label.pack()
    student_spin.pack()
    Clybutton.pack()
    metro_display.pack()

    mainwindow.mainloop()
initialpopup()
mainwindow()



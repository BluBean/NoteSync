import socket
#imports for GUI module
from tkinter import *
from functools import partial
import threading
#from playsound import playsound
import os
import sys
import sounddevice as sd
###################################
###Imports for DSP module
import soundfile as sf
## Import for metronome
import time

# Globals
S_PORT = 60002  # Reserve a port for your service.
ipadd = '18.220.239.193'  # ec2 server
#ipadd = '127.0.0.1'  # local

### select demo wav file ###
# vulf stems
#DEMO_WAV = 'Base_b90_t4_m9_o1.wav'
#DEMO_WAV = 'Guit_b90_t4_m9_o2.wav'
#DEMO_WAV = 'Pian_b90_t4_m9_o4.wav'
#DEMO_WAV = 'Theo_b90_t4_m9_o5.wav'
#DEMO_WAV = 'Drum_b90_t4_m9_o6.wav'

# voice stems
DEMO_WAV = 'vox1_b103_t4_m8_o0.wav'
#DEMO_WAV = 'vox2_b103_t4_m8_o1.wav'
#DEMO_WAV = 'vox3_b103_t4_m8_o2.wav'
#DEMO_WAV = 'vox4_b103_t4_m8_o3.wav'
#DEMO_WAV = 'vox5_b103_t4_m8_o6.wav'


##########################################################
#### Student Client Connection
#
###########################################################

"""# main student client code
def stu_main(student, host, file):
    s = socket.socket()  # Create a socket object

    # check for user input errors
    verify_inputs(student, file)

    # send the recorded file back to server
    with open (file,'rb') as f:
        # Send student number, get offset
        s.connect((host, S_PORT))
        s.send(str.encode(student))
        print("Sending student ID", student)

        # get and store metronome values in a list (bpm, num_measures, tot_measures)
        metronome = s.recv(11)
        print('metronome: ', metronome)

        bpm, t_sig, tot_measures = metronome.split(b',')
        print('bpm: ', bpm, 't_sig: ', t_sig, 'tot_measures: ', tot_measures)

        # get and store offset value for student (samples)
        offset = s.recv(1024)
        print('offset: ', offset)

        #change values to integers
        bpm, t_sig, tot_measures, offset = set_values(bpm,t_sig, tot_measures, offset)

        # record and save recording
        backgroundmetro(bpm, t_sig)
        offset_background(offset_state, offset, t_sig, bpm)
        #record(bpm, t_sig, tot_measures, offset, student)  # (<duration of recording>, <offset>) (samples)
        prerecorded_audio(bpm, t_sig, tot_measures, offset, student)  # for use during demos

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

    print('system exit')
    sys.exit(0)"""


#########################
### DEMO STUDENT CODE ###
#########################
def stu_main(student, host, file):
    global DEMO_WAV
    demo_wav = DEMO_WAV

    s = socket.socket()  # Create a socket object

    # check for user input errors
    verify_inputs(student, file)

    # send the recorded file back to server
    with open (demo_wav,'rb') as f:
        # Send student number, get offset
        s.connect((host, S_PORT))
        s.send(str.encode(student))
        print("Sending student ID", student)

        # get and store metronome values in a list (bpm, num_measures, tot_measures)
        metronome = s.recv(11)
        print('metronome: ', metronome)

        bpm, t_sig, tot_measures = metronome.split(b',')
        print('bpm: ', bpm, 't_sig: ', t_sig, 'tot_measures: ', tot_measures)

        # get and store offset value for student (samples)
        offset = s.recv(1024)
        print('offset: ', offset)

        #change values to integers
        bpm, t_sig, tot_measures, offset = set_values(bpm,t_sig, tot_measures, offset)

        # record and save recording
        backgroundmetro(bpm, t_sig)
        offset_background(offset_state, offset, t_sig, bpm)
        #record(bpm, t_sig, tot_measures, offset, student)  # (<duration of recording>, <offset>) (samples)
        prerecorded_audio(bpm, t_sig, tot_measures, offset, student)  # for use during demos

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

    print('system exit')
    sys.exit(0)


# add check to verify file exists or quit
def verify_inputs(student, file):

    # add check to verify file exists or quit
    if not os.path.exists(file):
        print(file + " does not exist. Exiting.")
        sys.exit(0)

    # check student id is between 0 and 9
    if int(student) > 9 or int(student) < 0:
        print("Student number is invalid. Valid student numbers are 0-9.")
        sys.exit(0)


def set_values(bpm, t_sig, tot_measures, offset):
    bpm = int(bpm)
    t_sig = int(t_sig)
    tot_measures = int(tot_measures)
    offset = int(offset)
    return bpm, t_sig, tot_measures, offset


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

def record(bpm, t_sig, tot_measures, offset, student):
    offset_size =60 * (t_sig / bpm)
    global red, gold, yellow, gnomestatus
    delay_display = (offset_size * offset)
    print('bpm: ', bpm, 't_sig: ', t_sig, 'tot_measures: ', tot_measures)
    # calculate recording length from GUI
    duration = t_sig * 60 * (tot_measures / bpm)  # length (unit: seconds)
    samples = 48000 * duration  # length to record based on GUI (unit: samples)
    offset_size = 48000 * 60 * (t_sig / bpm)  # samples per measure or known as the amount of samples in an offset
    fs = 48000  # Sample rate
    print('offset (samples): ', offset)
    # sd.rec(<length of recording in samples>, <samplerate>, <channels>)
    #threading.timer(delay_display,mainwindow.metro_display.configure(bg='red') ).start()
    myrecording = sd.rec(int(samples), samplerate=fs, channels=2)
    sd.wait()  # Wait until recording is finished
    # write('input1.wav', fs, myrecording)  # Save as WAV file
    sf.write('audio' + student + '.wav', myrecording, fs, subtype='PCM_16')
    print('voice recording saved')
    gnomestatus = False
    red = False
    gold = True
    yellow = False
    mainwindow.change_color(mainwindow)  #changes color to gold


#################
### FOR DEMOS ###
#################
def prerecorded_audio(bpm, t_sig, tot_measures, offset, student):
    offset_size =60 * (t_sig / bpm)
    global red, gold, yellow, gnomestatus
    global DEMO_WAV
    demo_wav = DEMO_WAV

    delay_display = (offset_size * offset)
    print('bpm: ', bpm, 't_sig: ', t_sig, 'tot_measures: ', tot_measures)
    # calculate recording length from GUI
    duration = t_sig * 60 * (tot_measures / bpm)  # length (unit: seconds)
    samples = 48000 * duration  # length to record based on GUI (unit: samples)
    offset_size = 48000 * 60 * (t_sig / bpm)  # samples per measure or known as the amount of samples in an offset
    fs = 48000  # Sample rate
    print('offset (samples): ', offset)
    # sd.rec(<length of recording in samples>, <samplerate>, <channels>)
    #threading.timer(delay_display,mainwindow.metro_display.configure(bg='red') ).start()
    red = True
    gold = False
    yellow = False
    mainwindow.change_color(mainwindow)  #changing color to red

    # play demo audio file
    samples, samplerate = sf.read(demo_wav)
    sd.play(samples, samplerate)
    sd.wait()  # Wait until recording is finished
    print("done playing audio")

    gnomestatus = False
    red = False
    gold = True
    yellow = False
    mainwindow.change_color(mainwindow)  #changes color to gold


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
    print("I'm in the metronome")
    while gnomestatus: # =True:
        counter += 1
        if counter == 1:
            print(f'TICK')
            #playsound('Tick.wav', False)
            metrovalue=metrovalue+1
            metrostatus.set(metrovalue)
        elif counter % tsig:
            print(f'tock')
            #playsound('tock.wav', False)
            metrovalue=metrovalue+1
            metrostatus.set(metrovalue)
        else:
            print(f'tock')
            #playsound('tock.wav', False)
            metrovalue=tsig
            metrostatus.set(metrovalue)
            metrovalue=0
            counter = 0

        time.sleep(sleep)
    if gnomestatus:
        background(metronome, bpm, tsig)
    metrostatus.set(0)

def offset_state(offset, tsig,bpm):
    global red, gold, yellow
    offset_delay = offset * tsig
    sleep = 60.0 / bpm
    count = 0
    while not count == offset_delay:
        count += 1
        time.sleep(sleep)

    red = True
    gold = False
    yellow = False
    print("changing color to red")
    mainwindow.change_color(mainwindow)  #changing color to red

def background(func, arg1, arg2):
    t = threading.Thread(target=func, args= (arg1, arg2))
    t.start()
def offset_background(func, arg1, arg2, arg3):
    t = threading.Thread(target=func, args= (arg1, arg2,arg3))
    t.start()

def backgroundmetro(bpm, tsig):
    global red, gold, yellow, gnomestatus
    red = False
    gold = False
    yellow = True
    mainwindow.change_color(mainwindow)
    metrovalue = 0
    sleep = 60.0 / bpm
    counter = 1
    if counter == 1:
        print(f'TICK')
        #playsound('Tick.wav', False)
        metrovalue = metrovalue + 1
        metrostatus.set(metrovalue)
        time.sleep(sleep)
        counter += 1
    while counter % int(tsig):
        print(f'tock')
        #playsound('tock.wav', False)
        metrovalue = metrovalue + 1
        metrostatus.set(metrovalue)
        time.sleep(sleep)
        counter += 1

    print(f'tock')
    #playsound('tock.wav', False)
    metrovalue = metrovalue + 1
    metrostatus.set(metrovalue)
    time.sleep(sleep)
    gnomestatus = True
    print("I called the metronome")
    background(metronome, bpm, tsig)


#############################
#Gui module
#############################

def initialpopup():
    Initialpopup = Tk()
    Initialpopup.title("Welcome to NoteSync")
    Initialpopup.iconbitmap("NoteSync_icon.ico")
    Initialpopup.config(background='#bca76a')
    logo = PhotoImage(file="NoteSync_Gold.png")
    label1 = Label(Initialpopup, image= logo, bg = "#bca76a")
    label1.pack()
    label2 = Label(Initialpopup, text ="Audio Synchronization Tool for Remote Learning", bg = "#bca76a")
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
    authors_label = Label(authors_name, text ="Notesync created by: Alec Dorn, Brandon Buccola, David Pivonka, Lance McKay, and Michael Moreno", bg = "#bca76a")
    authors_label.pack()
    mentor_label = Label(authors_name, text ="Program Mentor: Shamala Chickamenahalli", bg = "#bca76a")
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
            the indicator will be yellow for the countdown and then it will 
            turn red when the program is recording and you wil hear a
            metronome that is controlled by the teacher.
            
            4.All set! At the end of the recording, your audio file will 
            be sent to the teacher so that it can be combined with the 
            other singer's audio.
            
            Thank you for choosing NoteSync!!!!!!!!!
    """
    text_widget.insert(END, long_text)
    text_widget.configure(state='disabled')
    #gotit.pack(side=BOTTOM)


# command to run Client
def runClient(student, ipadd):
    #os.system('TestClient.py 2 18.220.239.193 audio2.wav')
    print(ipadd)
    stu = student.get()
    filename = 'audio' + stu + '.wav'
    f = open(filename, "w+")
    f.close()
    stu_main(stu, ipadd, filename)


class mainwindow:
    def __init__(self):
        global metro_display, ipadd
        mainwindow = Tk()
        mainwindow.title("NoteSync")
        mainwindow.iconbitmap("NoteSync_icon.ico")
        mainwindow.geometry("300x250")
        main_menu = Menu(mainwindow)
        mainwindow.config(background='#bca76a')
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


        # old ipadd location


        #filename = 'audio2.wav'
        current_value = '0'
        student_label = Label(mainwindow, text ="Select Student ID:", font=("32"), bg = "#bca76a")
        student_spin = Spinbox(mainwindow, from_ = 0, to = 9, wrap = True,width = 2, font=("helvetica 32"), bg = "#bca76a")

        Clybutton = Button(mainwindow, text="Run Client",font=("32"), command= partial( background,runClient,student_spin ,ipadd),bg = "#F6F6F6")
        global metrostatus
        metrostatus = IntVar()

        metro_display = Label(mainwindow, width=2, font=("helvetica", 45), bg = "#bca76a", textvariable=metrostatus) #, font=("Arial 32 bold"), bd = 0, fg = 'red')

        self.metro_display = metro_display

        var = IntVar()
        student_label.pack()
        student_spin.pack()
        Clybutton.pack()
        metro_display.pack()

        mainwindow.mainloop()

    # change display for metronome*******needs to be in mainwindow, please do not move****
    def change_color(self):
        if red:
            metro_display.configure(bg='red')
        if gold:
            metro_display.configure(bg="#bca76a")
        if yellow:
            metro_display.configure(bg='yellow')


initialpopup()
mainwindow()

#!/usr/bin/env python3

# Imports
import os, socket, sys
import threading
from _thread import *
from typing import List
import json
#imports for GUI module
from tkinter import *
from tkinter import filedialog
from functools import partial
from PIL import ImageTk as itk, Image
import threading
from playsound import playsound
import sounddevice as sd
from scipy.io.wavfile import write
## Import for metronome
import time


# Globals
HOST = '18.220.239.193'  # ec2 server
#HOST = '127.0.0.1'       # local host
T_PORT = 60003           # Reserve a port for your service.


###########################################################
#### Teacher Client Connection
#
###########################################################

# connect to server
def conn_server(s):
    s.connect((HOST, T_PORT))
    print("Connected.")


# close connection to server
def close_conn(s):
    print("Done Sending")
    s.shutdown(socket.SHUT_WR)
    print("Goodbye.")
    s.close()


# send teacher GUI data to server
def send_GUI_data(s, ids):

    # teacher GUI data
    metronome = pull_metronome()
    print('pull metronome: ', metronome)
    num_students = pull_num_students()
    print('pull num_students: ', num_students)
    offsets = pull_offsets(ids)
    print('pull offsets: ', offsets)

    # Send metronome
    s.send(bytes(metronome, 'utf-8'))
    print("Sent metronome info")

    # Send number of students (0-9)
    s.send(bytes(num_students, 'utf-8'))
    print("Sent num_students info")

    # Send offsets dictionary
    s.send(json.dumps(offsets, indent=2).encode('utf-8') + b"\n")
    print("Sent student offset info")

    print(s.recv(1024))

    return


# receive final mix as WAV
def receive_mix(s):

    # generate empty wav file
    f = open('NoteSync.wav', "w+")
    f.close()

    # Try to receive the WAV
    print("Receiving mixed wav file...")


    # write to corresponding student audio file
    with open(f"NoteSync.wav", "wb") as f:
        data = s.recv(4096)
        while data:
            print(f"Receiving {len(data)} bytes...")
            f.write(data)
            data = s.recv(4096)

    print("Done receiving.")
    s.send(b"sick mixtape G")
    print("close conn at receive_mix.")
    s.close()
    progress_var.set("Recording completed! Awaiting next command.")


###########################################################
#### Pull data from teacher client GUI
#    to send to server
###########################################################

# pull metronome values from GUI; store in a string
def pull_metronome() -> str:
    """
    Pull values from metronome.
    Values must be int with length == 3. ex: t_sig = 004

    bpm : bpm
    t_sig : time signature numerator
    tot_measures: total number of measures

    return as a string to send to server
    """
    bpm = int(bpm_slider.get())
    t_sig = int(time_sig_top.get())
    tot_measures = int(measures_slider.get())

    # bit manipulation
    if bpm < 10:
        bpm = "00"+str(bpm)
    elif bpm < 100:
        bpm = "0"+str(bpm)
    if t_sig <10:
        t_sig = "00" + str(t_sig)
    else:
        t_sig= "0"+str(t_sig)
    if tot_measures <10:
        tot_measures = "00" + str(tot_measures)
    else:
        tot_measures= "0"+str(tot_measures)

    print(str(bpm) + "," + str(t_sig) + "," + str(tot_measures))

    return str(bpm) + "," + str(t_sig) + "," + str(tot_measures)


# pull num_students value from GUI; store in a string
def pull_num_students() -> str:
    #returns single digit from 0-9
    student_number = int(ST.get())
    return str(student_number)  # test return
    #return str(num_students)


# pull student offset values from GUI; store in a dictionary
def pull_offsets(ids: List) -> dict:
    store = {}
    """
    Pull values from offset table.
    Store offset as string in dictionary (samples or measures)
    ids : student IDs
    return as a dictionary to send to server
    """
    store[0] = S0.get()
    store[1] = S1.get()
    store[2] = S2.get()
    store[3] = S3.get()
    store[4] = S4.get()
    store[5] = S5.get()
    store[6] = S6.get()
    store[7] = S7.get()
    store[8] = S8.get()
    store[9] = S9.get()
    return store


### main program ###
def teacher_main():
    # available student IDs
    ids = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    s = socket.socket()  # Create a socket object

    # connect and send data to server
    progress_var.set("Connecting to server...")
    conn_server(s)
    progress_var.set("Receiving mixed wav file...")
    send_GUI_data(s, ids)

    # wait to receive final wav file
    while True:
        notify = s.recv(4)  # waits for notification from server
        print("received notification: ", notify)
        if notify == b'done':
            break
        elif notify != b'done':
            s.close()
            print("Failed to receive notification")
            sys.exit(0)

    # try to receive wav
    receive_mix(s)


#############################
# Metronome module
#############################

    # Collect beats per minute and time signature from user
  #  bpm = int(input("Enter bpm value: "))
  #  tsig = int(input("Enter bpb value: "))

    # define metronome tool
def metronome(bpm, tsig):
    global gnomestatus
    sleep = 60.0 / bpm
    counter = 0
    while gnomestatus: # =True:
        counter += 1
        if counter % int(tsig):
            print(f'tock')
            playsound('tock.wav', False)
        else:
            print(f'TICK')
            playsound('Tick.wav', False)
            #mainwindow.after(1,start_stop(mainwindow.bpm_slider, mainwindow.time_sig_slider))
        time.sleep(sleep)
    if gnomestatus:
        background(metronome, bpm_slider, time_sig_top.get())

def background(func, arg1, arg2):
    t = threading.Thread(target=func, args= (arg1, arg2))
    t.start()


def run_background(func):
    t = threading.Thread(target=func)
    t.start()


#############################
#Gui module
#############################

def initialpopup():
    Initialpopup = Tk()
    Initialpopup.title("Welcome to NoteSync")
    Initialpopup.iconbitmap("NoteSync_icon.ico")
    Initialpopup.config(background='#99AAB5')

    logo = PhotoImage(file="NoteSync_logo.png")
    label1 = Label(Initialpopup, image= logo, bg = '#99AAB5')
    label1.pack()
    label2 = Label(Initialpopup, text ="Audio Synchronization Tool for Remote Learning", bg = '#99AAB5')
    label2.pack()
    #button1 = Button(Initialpopup, text="Get Started!", command = startrecording)
    button1 = Button(Initialpopup, text="Get Started!",command=Initialpopup.destroy ,bg = '#F6F6F6')
    button1.pack()
    #button2 = Button(Initialpopup, text="Stop Recording", command = stoprecording)
    #button2.pack()
    Initialpopup.mainloop()


def authors():
    authors_name = Tk()
    authors_name.title("Authors")
    authors_name.iconbitmap("NoteSync_icon.ico")
    authors_name.geometry("700x100")
    authors_name.config(background='#99AAB5')
    authors_label = Label(authors_name, text ="Notesync created by: Alec Dorn, Brandon Buccola, David Pivonka, Lance McKay, and Michael Moreno", bg = '#99AAB5')
    authors_label.pack()
    mentor_label = Label(authors_name, text="Program Mentor: Shamala Chickamenahalli", bg='#99AAB5')
    mentor_label.pack()
    authors = Button(authors_name, text="OK", command=authors_name.destroy, bg='#F6F6F6')
    authors.pack()
    authors_name.mainloop()


def help():
    tutorial = Tk()
    tutorial.title("Notesync User Guide")
    tutorial.iconbitmap("NoteSync_icon.ico")
    tutorial.geometry("700x500")
    # gotit = Button(tutorial, text="Thanks for the help!", command=tutorial.destroy)
    text_widget = Text(tutorial)  # , height=400, width=40
    # scroll_bar = Scrollbar(tutorial)

    # scroll_bar.pack(side=RIGHT, fill="y", expand=False)
    text_widget.pack(side=LEFT, fill="both", expand=True)
    # text_widget.config(yscrollcommand=scroll_bar.set)
    long_text = \
        """Please follow these steps to successfully operate NoteSync:

            1.Assign each student a number and provide this to them so 
            the student(s) can input their number in the student version 
            of the application.

            2.Select the Beats per minute that applies to your performance.

            3.Select the time signature that applies to your performance.

            4.Select the total number of measures in the performance.

            5.When ready, select the "Open Server" button.

            6.Immediately have each student select the "Run Client." 
            This action will start a countdown till the voice recording 
            starts for each student simultaneously. When finished, you 
            will receive all audio files ready to be synced.

            7.Press the "Sync Files" option after all recordings have been
            received to initiate the syncing function.

            8.All set! Check your program files for the resulting synced up
            file named "output.wav"

            If you would like to utilize the metronome, you can at any time
            by toggling the on and off button. You can also record your own 
            audio by selecting the "Record Voice File."

            Thank you for choosing NoteSync!!!!!!!!!
    """
    text_widget.insert(END, long_text)
    text_widget.configure(state='disabled')
    # gotit.pack(side=BOTTOM)
#button to start other modules


def start_stop(bpm, beats):
    global gnomestatus

    if var.get()== 1:
        gnomestatus = True
        metronome(bpm.get(), beats.get())
    else:
        gnomestatus = False
        metronome(bpm.get(), beats.get())


def mainwindow():
    global  bpm_slider, time_sig_top, measures_slider, ST
    global S0,S1, S2, S3, S4, S5, S6, S7, S8, S9, progress_var

    mainwindow = Tk()
    mainwindow.title("NoteSync")
    mainwindow.iconbitmap("NoteSync_icon.ico")
    mainwindow.geometry("600x400")
    main_menu = Menu(mainwindow)
    mainwindow.config(menu=main_menu)
    mainwindow.config(background='#99AAB5')

    #menu commands
    """def new_command():
        file_path0 = filedialog.askopenfilename()
    def save_command():
        file_path = filedialog.asksaveasfilename()
        file_selected = 1"""


    #create new menu options


    file_menu = Menu(main_menu)
    main_menu.add_cascade(label="Options",menu=file_menu)
    #file_menu.add_command(label="New...", command=new_command)
    #file_menu.add_command(label="Save Location", command=save_command)
    file_menu.add_command(label="Help", command=help)
    file_menu.add_command(label="Authors", command=authors)
    file_menu.add_command(label="Exit", command=mainwindow.quit)
    #BPM and time signature slider scale
    bpm_label = Label(mainwindow, text ="BPM", bg='#99AAB5')#, bg="red", fg ="gray")
    bpm_label.place(x=300, y=10)
    bpm_slider = Scale(mainwindow, from_=1, to=200, width=15,length = 200, orient=HORIZONTAL,  bg='#99AAB5') #, tickinterval=100,orient=HORIZONTAL)
    bpm_slider.set(100)
    bpm_slider.place(x=360, y=10)
    time_sig_label = Label(mainwindow, text ="Time Signature", bg='#99AAB5')#, bg="red", fg ="gray")
    time_sig_label.place(x=250, y=70)
    time_sig_top = Spinbox(mainwindow, from_ = 1, to = 16, width = 2,state = 'readonly',readonlybackground = '#99AAB5', font=("Arial 11"),wrap = True, bg='#99AAB5', bd=0)   #tickinterval=8,,orient=HORIZONTAL)
    time_sig_top.place(x=360, y=70)
    tsig_bar = Label(mainwindow, text="----", bg='#99AAB5')  # , bg="red", fg ="gray")
    tsig_bar.place(x=350, y=90)
    time_sig_bottom = Spinbox(mainwindow, from_ = 1, to = 8,values=(1,2,4,8),state = 'readonly',readonlybackground = '#99AAB5', width = 2, font=("Arial 11"), wrap = True, bg='#99AAB5', bd=0)   #,tickinterval=8,orient=HORIZONTAL)
    time_sig_bottom.place(x=360, y=110)
    measures_label = Label(mainwindow, text ="Total Measures", bg='#99AAB5')#, bg="red", fg ="gray")
    measures_label.place(x=250, y =140)
    measures_slider = Scale(mainwindow, from_=1, to=80, width=15,length = 200, orient=HORIZONTAL, bg='#99AAB5')
    measures_slider.place(x=360, y=150)
    # Student Information Section
    Delay_title = Label(mainwindow, text = "Select Student Information: ", font="helvetica 11", bg='#99AAB5')
    Delay_title.place(x=10, y=10)
    #Total Students Prompt
    student_amount = Label(mainwindow, text="Use up to Student ID :", bg='#99AAB5')
    student_amount.place(x=10, y=30)
    ST = Spinbox(mainwindow, from_=1, to=9, width=2, font=("Arial 11"), wrap=True, bg='#99AAB5', bd=0)
    ST.place(x=130, y=30)
    #Delay values prompts
    Delay0_label = Label(mainwindow, text ="Student 0 Delay :", bg='#99AAB5')
    Delay0_label.place(x=10, y=70)
    S0 = Spinbox(mainwindow, from_ = 0, to = 9, width = 2, font=("Arial 11"),wrap = True, bg='#99AAB5', bd=0)
    S0.place(x=130, y=70)
    Delay1_label = Label(mainwindow, text ="Student 1 Delay :", bg='#99AAB5')
    Delay1_label.place(x=10, y=90)
    S1 = Spinbox(mainwindow, from_ = 0, to = 9, width = 2, font=("Arial 11"),wrap = True, bg='#99AAB5', bd=0)
    S1.place(x=130, y=90)
    Delay2_label = Label(mainwindow, text ="Student 2 Delay :", bg='#99AAB5')
    Delay2_label.place(x=10, y=110)
    S2 = Spinbox(mainwindow, from_ = 0, to = 9, width = 2, font=("Arial 11"),wrap = True, bg='#99AAB5', bd=0)
    S2.place(x=130, y=110)
    Delay3_label = Label(mainwindow, text ="Student 3 Delay :", bg='#99AAB5')
    Delay3_label.place(x=10, y=130)
    S3 = Spinbox(mainwindow, from_ = 0, to = 9, width = 2, font=("Arial 11"),wrap = True, bg='#99AAB5', bd=0)
    S3.place(x=130, y=130)
    Delay4_label = Label(mainwindow, text ="Student 4 Delay :", bg='#99AAB5')
    Delay4_label.place(x=10, y=150)
    S4 = Spinbox(mainwindow, from_ = 0, to = 9, width = 2, font=("Arial 11"),wrap = True, bg='#99AAB5', bd=0)
    S4.place(x=130, y=150)
    Delay5_label = Label(mainwindow, text="Student 5 Delay :", bg='#99AAB5')
    Delay5_label.place(x=10, y=170)
    S5 = Spinbox(mainwindow, from_=0, to=9, width=2, font=("Arial 11"), wrap=True, bg='#99AAB5', bd=0)
    S5.place(x=130, y=170)
    Delay6_label = Label(mainwindow, text ="Student 6 Delay :", bg='#99AAB5')
    Delay6_label.place(x=10, y=190)
    S6 = Spinbox(mainwindow, from_ = 0, to = 9, width = 2, font=("Arial 11"),wrap = True, bg='#99AAB5', bd=0)
    S6.place(x=130, y=190)
    Delay7_label = Label(mainwindow, text ="Student 7 Delay :", bg='#99AAB5')
    Delay7_label.place(x=10, y=210)
    S7 = Spinbox(mainwindow, from_ = 0, to = 9, width = 2, font=("Arial 11"),wrap = True, bg='#99AAB5', bd=0)
    S7.place(x=130, y=210)
    Delay8_label = Label(mainwindow, text="Student 8 Delay :", bg='#99AAB5')
    Delay8_label.place(x=10, y=230)
    S8 = Spinbox(mainwindow, from_=0, to=9, width=2, font=("Arial 11"), wrap=True, bg='#99AAB5', bd=0)
    S8.place(x=130, y=230)
    Delay9_label = Label(mainwindow, text="Student 9 Delay :", bg='#99AAB5')
    Delay9_label.place(x=10, y=250)
    S9 = Spinbox(mainwindow, from_=0, to=9, width=2, font=("Arial 11"), wrap=True, bg='#99AAB5', bd=0)
    S9.place(x=130, y=250)

    #(whole measures)
    #record_button = Button(mainwindow, text='Record Voice File', command= partial(recorderlaunch,bpm_slider,time_sig_slider,measures_slider), bg='#99AAB5')
    #record_button.place(x=500, y=10)
    #start_server = Button(mainwindow, text='Open Server',command= serverlaunch, bg='#F6F6F6') #,command= partial(recorderlaunch,bpm_slider,time_sig_slider,measures_slider))
    #start_server.place(x=500, y=150)
    #sync_files=Button(mainwindow, text='Sync Files', command=partial(DSPlaunch, bpm_slider,time_sig_slider,measures_slider), bg='#F6F6F6')
    #sync_files.place(x=525, y=50)
    #send_data = Button(mainwindow, text='Send Data',command= sendit, bg='#F6F6F6') #,command= partial(recorderlaunch,bpm_slider,time_sig_slider,measures_slider))
    #send_data.place(x=600, y=150)
    Run_Program = Button(mainwindow, text='Run', font="helvetica 11", command=partial(run_background,teacher_main), bg='#F6F6F6')
    Run_Program.place(x=277, y=340)
    # global play
    image = Image.open('Play_button.png')
    image2 = Image.open('Pause_button.png')
    resize_image = image.resize((50,50))
    resize_image2 = image2.resize((50,50))
    off = itk.PhotoImage(resize_image)
    on = itk.PhotoImage(resize_image2)
    global var
    var = IntVar()
    play = Checkbutton(mainwindow, image=off, selectimage=on,indicatoron=False,bd = 0,variable=var, command=partial(background,start_stop, bpm_slider,time_sig_top), bg='#99AAB5')
    play.place(x=270, y=270)
    progress_var = StringVar()
    progress_label = Label(mainwindow, textvariable = progress_var, bg='#99AAB5')
    progress_label.place(x=320, y=345)

    mainwindow.mainloop()

initialpopup()
mainwindow()


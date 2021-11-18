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

    def record(rec_samples, offset):
        #print('checkpoint recorder')
        mainwindow.metro_display.configure(bg='red')
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
        offset = s.recv(1024)  # get and store offset value for student (samples)
        #print(offset)
        metronome = s.recv(1024)  # get and store metronome values in a list (bpm, num_measures, tot_measures)
        print(metronome)
        bpm, num_measures, tot_measures = metronome.split(b',')
        print('bpm: ', bpm, 'num_measures: ', num_measures, 'tot_measures: ', tot_measures)
        # record and save recording

        record(240000, offset)  # (<duration of recording>, <offset>) (samples)

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
#### Client MODULE
###########################################################
###########################################################
#### Various functions
###########################################################


###########################################################
####DSP MODULE
###########################################################
class dsp:
    """
    sf1 = sf.SoundFile('audio1.wav')
    print('samples = {}'.format(sf1.frames))
    print('sample rate = {}'.format(sf1.samplerate))
    print('seconds = {}'.format(sf1.frames / sf1.samplerate))
    ls1 = sf1.frames
    print(ls1)

    sf2 = sf.SoundFile('audio2.wav')
    print('samples = {}'.format(sf2.frames))
    print('sample rate = {}'.format(sf2.samplerate))
    print('seconds = {}'.format(sf2.frames / sf2.samplerate))
    ls2 = sf2.frames
    print(ls2)
    """

    #################################################################
    # Calculates offset required
    #
    # --- inputs:
    # beats = beats per measure (from selected time signature)
    # num_meas = number of measures from song start
    #                     to when student begins
    # bpm = beats per minute (tempo)
    #
    # --- output:
    # duration = milliseconds of buffer required
    #################################################################
    def syncfiles(bpm, beats, num_meas):
        def testvariables(bpm, beats, num_meas):
            print ("this is test of gui sliders \n bpm = ", bpm,"\n beats= ", beats,"\n measures= ", num_meas)
        def calc_duration(bpm, beats, num_meas):
            duration = beats * (num_meas / bpm)
            print('duration: ', duration)

        def read_audio(audio_file):
            rate, data = sf.read(audio_file)  # Return the sample rate (in samples/sec) and data from a WAV file
            return data, rate


        s1, fs1 = sf.read('audio1.wav')  # get data, samplerate
        info1 = sf.info('audio1.wav')
        # bits1 = sf.samplerate('audio1.wav')
        print(info1)

        s2, fs2 = sf.read('audio2.wav')
        info2 = sf.info('audio2.wav')
        # bits2 = sf.samplerate('audio2.wav')
        print('\n', info2)
        # print(s1, fs1, s2, fs2)

        # e = s1-s2 # difference signal
        l1 = len(s1)  # total number of samples
        l2 = len(s2)
        print(l1, l2)
        max_samples = max(l1, l2)  # file with greatest number of samples
        min_samples = min(l1, l2)
        samples_offset = abs(max_samples - min_samples)
        print(samples_offset)

        # add buffer to beginning of shorter audio file
        buffer = np.zeros(samples_offset)  # generate buffer
        # print(buffer)

        sf.write('buffer.wav', buffer, 48000)  # create buffer .wav file
        audio = AudioSegment.from_file('audio1.wav', format="wav")  # open both .wav files to write
        buffer_audio = AudioSegment.from_file('buffer.wav', format="wav")
        combined = buffer_audio + audio  # audio with buffer appended at beginning
        file_handle = combined.export("buffered_audio.wav", format="wav")  # export buffered wav file

        audio1 = AudioSegment.from_file("audio2.wav", format="wav")
        audio2 = AudioSegment.from_file("buffered_audio.wav", format="wav")
        boost1 = audio1 + 9  # audio1 x dB louder (clipping)
        overlay = boost1.overlay(audio2, position=0)  # Overlay audio2 over audio1
        file_handle = overlay.export("buffered_overlay.wav", format="wav")  # export overlaid wav files
        testvariables(bpm, beats, num_meas)

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

    ## record(<samples in recording>, <samples in offset>)
"""def record(rec_samples, offset):
    metro_display.configure(bg='red')        
    fs = 48000  # Sample rate
    duration = rec_samples  # Duration of recording (samples)
    print('offset (samples): ', offset)
    # sd.rec(<length of recording in samples>, <samplerate>, <channels>)
    myrecording = sd.rec(int(duration), samplerate=fs, channels=2)
    sd.wait()  # Wait until recording is finished
    # write('input1.wav', fs, myrecording)  # Save as WAV file
    sf.write('audio' + student + '.wav', myrecording, fs, subtype='PCM_16')
    print('voice recording saved')
    metro_display.configure(bg='blue')"""

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

    logo = PhotoImage(file="NoteSync_logo.png")
    label1 = Label(Initialpopup, image= logo)
    label1.pack()
    label2 = Label(Initialpopup, text ="Audio Synchronization Tool for Remote Learning")
    label2.pack()
    #button1 = Button(Initialpopup, text="Get Started!", command = startrecording)
    button1 = Button(Initialpopup, text="Get Started!",command=Initialpopup.destroy )
    button1.pack()
    #button2 = Button(Initialpopup, text="Stop Recording", command = stoprecording)
    #button2.pack()
    Initialpopup.mainloop()

def authors():
    authors_name = Tk()
    authors_name.title("Authors")
    authors_name.iconbitmap("NoteSync_icon.ico")
    authors_name.geometry("700x100")
    authors_label = Label(authors_name, text ="Notesync created by: Alec Dorn, Brandon Buccola, David Pivonka, Lance McKay, and Michael Moreno")
    authors_label.pack()
    mentor_label = Label(authors_name, text ="Program Mentor: Shamala Chickamenahalli")
    mentor_label.pack()
    authors = Button(authors_name, text="OK", command=authors_name.destroy)
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

def DSPlaunch(bpm, beats, num_meas):
    #print('sync files button worked')
    dsp.syncfiles(bpm.get(), beats.get(), num_meas.get())


def mainwindow():
    mainwindow = Tk()
    mainwindow.title("NoteSync")
    mainwindow.iconbitmap("NoteSync_icon.ico")
    mainwindow.geometry("300x200")
    main_menu = Menu(mainwindow)
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
    ipadd = '18.220.239.193'
    #filename = 'audio2.wav'
    current_value = '0'
    student_label = Label(mainwindow, text ="Student number select", font=("32"))
    student_spin = Spinbox(mainwindow, from_ = 0, to = 9, wrap = True,width = 2, font=("Arial 32"))

    Clybutton = Button(mainwindow, text="Run Client",font=("32"), command= partial( background,runClient,student_spin ,ipadd))
    global metrostatus
    metrostatus = IntVar()

    metro_display = Label(mainwindow, width=2, font=("Arial", 45),bg='blue', textvariable=metrostatus) #, font=("Arial 32 bold"), bd = 0, fg = 'red')

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



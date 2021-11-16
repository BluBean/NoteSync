########################################
#Main GUI for Notesync
#    Last edited 10/25/2021 @18:16 MST time
#
########################################
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

####Imports for recorder module already called

#### Imports for server module
import socket  # Import socket module


###########################################################
#### Server MODULE
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
class voicerecorder:
    ## record(<samples in recording>, <samples in offset>)
    def record(rec_samples, offset):
        fs = 48000  # Sample rate
        duration = rec_samples  # Duration of recording (samples)
        print('offset (samples): ', offset)
        # sd.rec(<length of recording in samples>, <samplerate>, <channels>)
        myrecording = sd.rec(int(duration), samplerate=fs, channels=2)
        sd.wait()  # Wait until recording is finished
        # write('input1.wav', fs, myrecording)  # Save as WAV file
        sf.write('test.wav', myrecording, fs, subtype='PCM_16')
        print('voice recording saved')

#############################
# Metronome module
#############################
class gnome:
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
            if counter % tsig:
                print(f'tock')
                playsound('tock.wav', False)
            else:
                print(f'TICK')
                playsound('Tick.wav', False)
                time.sleep(sleep)
                mainwindow.after(1,start_stop(bpm_slider, time_sig_slider))
            time.sleep(sleep)

def background(func, arg1, arg2):
    t = threading.Thread(target=func, args= (arg1, arg2))
    t.start()

    # run metronome tool with given values
    #metronome(bpm, tsig)
#############################
#Gui module
#############################





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

mainwindow = Tk()
mainwindow.title("NoteSync")
mainwindow.iconbitmap("NoteSync_icon.ico")
mainwindow.geometry("700x700")
main_menu = Menu(mainwindow)
mainwindow.config(menu=main_menu)
mainwindow.config(background='gray')

#menu commands
def new_command():
    file_path0 = filedialog.askopenfilename()
def save_command():
    file_path = filedialog.asksaveasfilename()
    file_selected = 1

#create new menu options

file_menu = Menu(main_menu)
main_menu.add_cascade(label="File",menu=file_menu)
file_menu.add_command(label="New...", command=new_command)
file_menu.add_command(label="Save Location", command=save_command)
file_menu.add_command(label="Authors", command=authors)
file_menu.add_command(label="Exit", command=mainwindow.quit)
#BPM and time signature slider scale
bpm_label = Label(mainwindow, text ="Beats Per Minute")#, bg="red", fg ="gray")
bpm_label.pack()
bpm_slider = Scale(mainwindow, from_=1, to=200) #, tickinterval=100,orient=HORIZONTAL)
bpm_slider.set(100)
bpm_slider.pack()
time_sig_label = Label(mainwindow, text ="Time Signature Numerator")#, bg="red", fg ="gray")
time_sig_label.pack()
time_sig_slider = Scale(mainwindow, from_=1, to=16,orient=HORIZONTAL, bg = 'gray')   #tickinterval=8,,orient=HORIZONTAL)
time_sig_slider.set(4)
time_sig_slider.pack()
time_sigd_label = Label(mainwindow, text ="Time Signature Denominator")#, bg="red", fg ="gray")
time_sigd_label.pack()
time_sigd_slider = Scale(mainwindow, from_=1, to=8,orient=HORIZONTAL, bg = 'gray')   #,tickinterval=8,orient=HORIZONTAL)
time_sigd_slider.set(4)
time_sigd_slider.pack()
measures_label = Label(mainwindow, text ="Total Measures")#, bg="red", fg ="gray")
measures_label.pack()
measures_slider = Scale(mainwindow, from_=1, to=80,orient=HORIZONTAL, bg = 'gray')   #,tickinterval=8,orient=HORIZONTAL)
measures_slider.set(0)
measures_slider.pack()
# Dropbox for delays
Delay1_label = Label(mainwindow, text ="Student 1 Delay (whole measures)")
Delay1_label.pack()
S1 = Spinbox(mainwindow, from_ = 0, to = 9)
S1.pack()
Delay2_label = Label(mainwindow, text ="Student 2 Delay (whole measures)")
Delay2_label.pack()
S2 = Spinbox(mainwindow, from_ = 0, to = 9)
S2.pack()
Delay3_label = Label(mainwindow, text ="Student 3 Delay (whole measures)")
Delay3_label.pack()
S3 = Spinbox(mainwindow, from_ = 0, to = 9)
S3.pack()
Delay4_label = Label(mainwindow, text ="Student 4 Delay (whole measures)")
Delay4_label.pack()
S4 = Spinbox(mainwindow, from_ = 0, to = 9)
S4.pack()
Delay5_label = Label(mainwindow, text ="Student 5 Delay (whole measures)")
Delay5_label.pack()
S5 = Spinbox(mainwindow, from_ = 0, to = 9)
S5.pack()
#button to start other modules
def recorderlaunch(bpm, beats, num_meas):
    print('Recording in progress')
    rec_length = beats.get() * (num_meas.get() / bpm.get()) #length in seconds
    samples = 48000 * 60 * rec_length  #length to record based on GUI (samples)
    offset_size = 48000 * 60 * (beats.get()/bpm.get())  # samples per measure or known as the amount of samples in an offset
    voicerecorder.record(samples, offset_size)  # args  record(<samples in recording>, <samples in offset>)

def DSPlaunch(bpm, beats, num_meas):
    #print('sync files button worked')
    dsp.syncfiles(bpm.get(), beats.get(), num_meas.get())

def start_stop(bpm, beats):
    global gnomestatus
    if var.get()== 1:
        gnomestatus = True
        gnome.metronome(bpm.get(), beats.get())
    else:
        gnomestatus = False
        gnome.metronome(bpm.get(), beats.get())

record_button = Button(mainwindow, text='Record Voice File', command= partial(recorderlaunch,bpm_slider,time_sig_slider,measures_slider)).pack()
Button(mainwindow, text='Sync Files', command=partial(DSPlaunch, bpm_slider,time_sig_slider,measures_slider)).pack()
# global play
image = Image.open('Off.png')
image2 = Image.open('On.png')
resize_image = image.resize((100,50))
resize_image2 = image2.resize((100,50))
off = itk.PhotoImage(resize_image)
on = itk.PhotoImage(resize_image2)
var = IntVar()
play = Checkbutton(mainwindow, image=off, selectimage=on,indicatoron=False,bd = 0,variable=var, command=partial(background,start_stop, bpm_slider,time_sig_slider)).pack()

#play = Button(mainwindow, bd = 0, image = off, command=partial(start_stop, bpm_slider,time_sig_slider)).pack()
#Opening the maintask window with some random stuff to fil the window
#two = Label(mainwindow, text ="TBD", bg="green", fg ="black")
#two.pack(fill=X)
three = Label(mainwindow, text ="TBD", bg="blue", fg ="white")
three.pack(side=LEFT, fill=Y)

mainwindow.mainloop()





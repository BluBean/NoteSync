Backend overview
  1.	Calculate: total number of samples for (future) recorded audio file using metronome info and max measures info
  2.	Calculate: student offset using metronome info & measure offset (per student) input by teacher
  3.	Calculate: student recording length = total samples of audio file – student offset samples
  4.	Server receives student connection and student number
  5.	Send student offset & recording length
  6.	Student hears one measure of metronome clicks before recording starts
  7.	Start recording
  8.	Stop recording when student recording length reached
  9.	Send .wav to server
  10.	Pad beginning of .wav file to equal total number of samples
  11.	Overlay .wav files (normalize?)
  12.	Send single overlaid .wav file to teacher


Server
  Start_process()
    1.	Main code for server

  Calc_offsets()
    1.	Receive metronome/GUI data (from teacher)
    2.	Perform backend steps 1-3
    3.	Return offset data and student record length as dictionary
    4.	Send to send_data()

  Send_data(offsets)
    1.	Backend steps 4 and 5

wait for student to finish recording
  •	Steps 6-9 are done client side

    2.	Receive audio file from student
    3.	Done receiving
    4.	Close connection

  Sync_files()
    1.	Read received audio files
    2.	Backend steps 10-12 (maybe don’t put step 12 in this function)

Client
  1.	Enter student number (0-9)
  2.	Verify valid number
  3.	Send student number to server
  4.	Receive student offset and recording length
  5.	One measure of metronome then start recording
  6.	Automatically finish recording
  7.	Send audio file to server

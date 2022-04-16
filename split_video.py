import numpy as np
import matplotlib.pyplot as plt
from moviepy.editor import *
import os
import librosa
import time
#import IPython.display as ipd
import simpleaudio as sa

def plotaudio(y):
    plt.plot(y)
    plt.show()

def plot2im ( y ):
    fig=plt.figure()
    plt.plot(y)
    fig.canvas.draw ( )
 
    # Get the RGBA buffer from the figure
    w,h = fig.canvas.get_width_height()
    buf = np.fromstring ( fig.canvas.tostring_argb(), dtype=np.uint8 )
    buf.shape = ( h, w,4 )
    #get only BGR (opencv pattern)
    buf=buf[:,:,[3,2,1]]

    return buf

def nothing(val):
    pass
def viewFrame(num):
    if not play:
        cap.set(cv2.CAP_PROP_POS_FRAMES, num)
        ret, frame = cap.read()
        cv2.imshow('video',frame)

import crepe
from scipy.io import wavfile

from pathlib import Path
 
instruments={}
rootdir = 'instruments'
instrument_paths= [ path for path in Path(rootdir).iterdir() if path.is_dir()]
for ip in instrument_paths:
    instrument_videos=[video for video in ip.iterdir() if video.is_file()]
    if len(instrument_videos)>0:
        instruments[ip.name]=instrument_videos


print(instruments)

vName='flauta.mp4'

video = VideoFileClip(vName)
audio = video.audio
h,w=video.size
fps=video.fps
print('video size ',w,'x',h,', at ',fps,' fps.')
t=audio.duration
sr=audio.fps
print('audio duration: ',t,', sampling rate: ',sr)
audio.write_audiofile("audio.mp3")
y=audio.to_soundarray(fps=sr)
filename = librosa.util.example_audio_file()

# 2. Load the audio as a waveform `y`
#    Store the sampling rate as `sr`
#y, sr = librosa.load(filename)
y=librosa.core.to_mono(np.transpose(y))
#y_harmonic, y_percussive = librosa.effects.hpss(y)




time, frequency, confidence, activation = crepe.predict(y, sr, viterbi=True)
import matplotlib.pyplot as plt
from scipy.signal import medfilt
mfr=medfilt(frequency,11)
midi=69+12*np.log2(mfr/440)
mcon=medfilt(confidence,11)
plt.plot(time,midi)
plt.plot(time,np.min(midi)+mcon*(np.max(midi)-np.min(midi)))
plt.show()



import pandas as pd
threshold=0.8
tune_thresh=0.3#in midi
registeringNote=False
notas = {'midi':[],'inicio':[],'fim':[],'duracao':[],'i':[],'j':[],'avg conf':[],'std dev':[]}
notas = pd.DataFrame(notas)
print(notas)
for i in range(time.shape[0]):
    if confidence[i]>threshold:
        if not registeringNote:
            registeringNote=True
            row=pd.DataFrame({'midi':[midi[i]],'inicio':[time[i]],'i':[i]})            
            #print(row)
            notas=notas.append(row, ignore_index=True)
            #print(notas.tail(1))

            #note start
        else:
            pass
    else:
        if registeringNote:
            registeringNote=False
            notas.at[notas.index[-1],'j']=i
            notas.at[notas.index[-1],'fim']=time[i]
            notas.at[notas.index[-1],'duracao']=notas.at[notas.index[-1],'fim']-notas.at[notas.index[-1],'inicio']
            notas.at[notas.index[-1],'avg conf']=np.average(confidence[int(notas.at[notas.index[-1],'i']):i])
            #print(notas.tail(1))
            #note end
        else:
            pass
print(notas)
#demove low duration notes
durThresh=0.1
indexLowDur = notas[ notas['duracao'] < durThresh ].index
notas=notas.drop(indexLowDur , inplace=False)
print(notas)
#remove out of tune notes
tuneThresh=0.3
for index, row in notas.iterrows():
    i=int(notas.at[index,'i'])
    j=int(notas.at[index,'j'])
    note=int(round(np.average(midi[i:j])))
    std = np.sqrt(np.average(abs(midi[i:j] - note)**2))#std deviation
    #print(np.abs(midi[i:j]-note)<tuneThresh)
    notesThatPassed=np.abs(midi[i:j]-note)<tuneThresh
    if not all(notesThatPassed):
        #remove that line         
        notas=notas.drop(index , inplace=False)
    else:
        notas.at[index,'midi']=note
        notas.at[index,'std dev']=std

print(notas)
notas.to_csv(r'flauta.csv', index = False)




#!pip install moviepy
import subprocess as sp
from moviepy.editor import *
import os
recorder = VideoFileClip("flauta.mp4")

song_midi={'midi':[72, 72, 74, 72, 77, 76],'start':[0.0,0.05,0.1,0.3,0.4,0.5],'end':[0.05,0.1,0.3,0.4,0.5,0.7]}
print(song_midi['midi'])
clips=[]
for i in range(len(song_midi['midi'])):
    this_note=notas.loc[notas['midi'] == song_midi['midi'][i]]#select with correct midi value
    dur=song_midi['end'][i]-song_midi['start'][i]
    this_note=this_note.loc[this_note['duracao'] >= dur]#select with the right duration
    this_note=this_note[this_note['std dev'] == this_note['std dev'].max()] 
    startime=this_note.at[this_note.index[-1],'inicio']
    endtime=startime+dur 
    noteClip=recorder.subclip(startime,endtime)#this_note['inicio'],this_note['inicio']+dur)
    noteClip=noteClip.set_start(song_midi['start'][i])
    clips.append(noteClip)
cc = CompositeVideoClip(clips)
cc.write_gif("test.gif")
#cc.set_duration(0.5).write_videofile("happytest.mp4")
cc.write_videofile("happytest.mp4")
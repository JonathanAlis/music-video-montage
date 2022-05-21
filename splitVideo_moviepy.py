import numpy as np
import matplotlib.pyplot as plt
from moviepy.editor import *
import sys
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
filename = librosa.util.example('brahms')

# 2. Load the audio as a waveform `y`
#    Store the sampling rate as `sr`
#y, sr = librosa.load(filename)
y=librosa.core.to_mono(np.transpose(y))
#y_harmonic, y_percussive = librosa.effects.hpss(y)

pitches,mags=librosa.core.pitch.piptrack(y, sr=sr, n_fft=2048, hop_length=512,
             fmin=70.0, fmax=600.0, threshold=0.1,
             win_length=None, window='hann', center=True, pad_mode='reflect',
             ref=None)
#imgplot = plt.imshow(pitches)
#plt.show()
#ipd.Audio(y,rate=sr) 
# Start playback
audio=y* 32767 / max(abs(y))
audio = audio.astype(np.int16)
play_obj = sa.play_buffer(audio, 1, 2, sr)

print(np.amax(y))
#print((audio.shape()))
# Wait for playback to finish before exiting


import crepe
from scipy.io import wavfile

sr, audio = wavfile.read('audio.wav')
time, frequency, confidence, activation = crepe.predict(audio, sr, viterbi=True)
print(time)
print(frequency)
print(confidence)
print(activation)
#pYIN
import matplotlib.pyplot as plt
plt.plot(time,frequency)
plt.show()
import os, sys
dir = os.path.dirname(os.path.realpath(__file__))
srcpath = dir+'/pypYIN-master/src'
sys.path.append(srcpath)

import pYINmain
import essentia.standard as ess
import numpy as np
from YinUtil import RMS

filename1 = 'audio.wav'
fs = 44100
frameSize = 2048
hopSize = 256

pYinInst = pYINmain.PyinMain()
pYinInst.initialise(channels = 1, inputSampleRate = fs, stepSize = hopSize, blockSize = frameSize,
                lowAmp = 0.25, onsetSensitivity = 0.7, pruneThresh = 0.1)

# frame-wise calculation
audio = ess.MonoLoader(filename = filename1, sampleRate = fs)()

for frame in ess.FrameGenerator(audio, frameSize=frameSize, hopSize=hopSize):
        fs = pYinInst.process(frame)

# calculate smoothed pitch and mono note
monoPitch = pYinInst.getSmoothedPitchTrack()

# output smoothed pitch track
print('pitch track')
for ii in fs.m_oSmoothedPitchTrack:
    print((ii.values))
print('\n')

fs = pYinInst.getRemainingFeatures(monoPitch)

# output of mono notes,
# column 0: frame number,
# column 1: pitch in midi numuber, this is the decoded pitch
# column 2: attack 1, stable 2, silence 3
print('mono note decoded pitch')
for ii in fs.m_oMonoNoteOut:
    print((ii.frameNumber, ii.pitch, ii.noteState))
print('\n')

print('note pitch tracks')
for ii in fs.m_oNotePitchTracks:
    print(ii)
print('\n')

# median pitch in Hz of the notes
print('median note pitch')
for ii in fs.m_oNotes:
    print((ii.values))
print ('\n')


play_obj.wait_done()
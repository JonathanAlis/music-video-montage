import cv2
import numpy as np
import wave
import struct
import matplotlib.pyplot as plt
from moviepy.editor import *
import sys
import librosa
import time
    
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
vName='trombone.mp4'

video = VideoFileClip(vName)
audio = video.audio
h,w=video.size
fps=video.fps
print('video size ',w,'x',h,', at ',fps,' fps.')


cv2.waitKey()
#audio.write_audiofile(sys.argv[2]) # 4.


cap=cv2.VideoCapture(vName)
print(cap)
w= int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h= int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps=  int(cap.get(cv2.CAP_PROP_FPS))
numFrames=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print('video size ',w,'x',h,', at ',fps,' fps. ',numFrames, ' frames.')
cv2.namedWindow('video',cv2.WND_PROP_FULLSCREEN)
cv2.createTrackbar('time Now','video',0,numFrames,viewFrame)
cv2.createTrackbar('init','video',0,numFrames,viewFrame)
cv2.createTrackbar('until','video',numFrames,numFrames,viewFrame)
init=0
until= numFrames
play=False
playingFrame=0


audioFile='audio.wav'
y, sr = librosa.load(audioFile)
#print(y.shape)
#plt.show() 

im = plot2im ( y )
im=cv2.resize(im,(w,h))
success, frame = cap.read()
if not success:
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
final = cv2.hconcat([frame, im])
cv2.imshow('video',final)
key=cv2.waitKey() & 0xFF
while(cap.isOpened()):   
    print(playingFrame)
    print(play)
    #read the frame and show it
    #cap.set(cv2.CAP_PROP_POS_FRAMES, playingFrame)
    
    #get the time stamps for 
    startAtFrame=cv2.getTrackbarPos('init','video')
    endAtFrame=cv2.getTrackbarPos('until','video')
    timeStart=startAtFrame/fps
    timeEnd=endAtFrame/fps
    
    if play:
        cv2.setTrackbarPos('time Now','video',playingFrame)
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, startAtFrame)
        cv2.imshow('video',frame)
        playingFrame=playingFrame+1    
        timeNow=playingFrame/fps 
        dt=time.time()-t
        print(1000/fps-dt*1000)#mili seconds
        if int(1000/fps-dt*1000)>0:
            key=cv2.waitKey(int(1000/fps-dt*1000)) & 0xFF
        else:
            key=cv2.waitKey(1) & 0xFF
            #print(1/(time.time()-t))
        t=time.time()       
        if playingFrame>=endAtFrame:
            print(playingFrame,timeEnd)
            play=False
            cap.set(cv2.CAP_PROP_POS_FRAMES, startAtFrame)
            playingFrame=startAtFrame
            print('ended')

    else:
        key=cv2.waitKey() & 0xFF
    
    if key == ord('q'):
        break
    elif key == ord('p'):
        if play==False:
            play=True
            t=time.time()
            #cap.set(cv2.CAP_PROP_POS_FRAMES, startAtFrame)
            #audio=y[int(timeStart*sr):int(timeEnd*sr)]
            #print(audio.shape)
        else:
            play=False
    elif key == ord('r'):
        play=True
        t=time.time()
        cap.set(cv2.CAP_PROP_POS_FRAMES, startAtFrame)
        playingFrame=startAtFrame
    key = ord('n')

frequency = 1000
num_samples = 48000
sampling_rate = 48000.0
amplitude = 16000
file = "test.wav"
sine_wave = [np.sin(2 * np.pi * frequency * x/sampling_rate) for x in range(num_samples)]
nframes=num_samples
comptype="NONE"
compname="not compressed"
nchannels=1
sampwidth=2
#wav_file=wave.open(file, 'w')
#wav_file.setparams((nchannels, sampwidth, int(sampling_rate), nframes, comptype, compname))
#for s in sine_wave:
    #wav_file.writeframes(struct.pack('h', int(s*amplitude)))
#wav_file.close()
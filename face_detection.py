import numpy as np
import matplotlib.pyplot as plt
from moviepy.editor import *
import librosa
from scipy.signal import medfilt
#import simpleaudio as sa
import pandas as pd
import crepe
from scipy.io import wavfile
import face_recognition
from pathlib import Path

def avg_eyes_pos(video, time, show=False):
    """
    video: mp4 file
    time: tuple(start, end)
    """
    clip = VideoFileClip(video)
    left_x=[]
    left_y=[]
    right_x=[]
    right_y=[]
    for t in np.arange(time[0], time[1], 1/clip.fps):
        try:
            frame = clip.get_frame(t)
        except:
            continue
        face_landmarks_list = face_recognition.face_landmarks(frame)
        if len(face_landmarks_list)>0:
            left_x.append(np.mean([x for (x,y) in face_landmarks_list[0]['left_eye']]))
            left_y.append(np.mean([y for (x,y) in face_landmarks_list[0]['left_eye']]))
            right_x.append(np.mean([x for (x,y) in face_landmarks_list[0]['right_eye']]))
            right_y.append(np.mean([y for (x,y) in face_landmarks_list[0]['right_eye']]))
    left_x=np.median(left_x) 
    left_y=np.median(left_y)
    right_x=np.median(right_x)
    right_y=np.median(right_y)
    
    return [[left_x,left_y],[right_x,right_y]]
        
        
#eyes= avg_eyes_pos('instruments/recorder/flauta.mp4', (3, 4), show=True)
#print(eyes)



def video_note_split(vName,threshold=0.8, tune_thresh=0.3,dur_thresh=0.1, show_notes=False):
    """
    vName: string ending with .mp4 that contains the video with the notes
    creates a csv file cointaining the starting and ending of all notes
    """
    
    video = VideoFileClip(vName)
    audio = video.audio
    h,w=video.size
    fps=video.fps
    print('video size ',w,'x',h,', at ',fps,' fps.')
    t=audio.duration
    sr=audio.fps
    print('audio duration: ',t,', sampling rate: ',sr)
    y=audio.to_soundarray(fps=sr)

    y=librosa.core.to_mono(np.transpose(y))
    #y_harmonic, y_percussive = librosa.effects.hpss(y)
    time, frequency, confidence, activation = crepe.predict(y, sr, viterbi=True)
    mfr=medfilt(frequency,21)
    midi=69+12*np.log2(mfr/440)
    mcon=medfilt(confidence,21)
    if show_notes:
        plt.plot(time,midi)
        plt.plot(time,np.min(midi)+mcon*(np.max(midi)-np.min(midi)))
        plt.show()

    registeringNote=False
    notas = {'midi':[],'inicio':[],'fim':[],'duracao':[],'i':[],'j':[],'avg conf':[],'std dev':[],'eye_pos':[]}
    notas = pd.DataFrame(notas)
    for i in range(time.shape[0]):
        if confidence[i]>threshold:
            if not registeringNote:
                registeringNote=True
                row=pd.DataFrame({'midi':[midi[i]],'inicio':[time[i]],'i':[i]})            
                notas=notas.append(row, ignore_index=True)
            else:
                pass
        else:
            if registeringNote:
                registeringNote=False
                notas.at[notas.index[-1],'j']=i
                notas.at[notas.index[-1],'fim']=time[i]
                notas.at[notas.index[-1],'duracao']=notas.at[notas.index[-1],'fim']-notas.at[notas.index[-1],'inicio']
                notas.at[notas.index[-1],'avg conf']=np.average(confidence[int(notas.at[notas.index[-1],'i']):i])
                eyes= avg_eyes_pos(vName,(notas.at[notas.index[-1],'inicio'],notas.at[notas.index[-1],'fim']), show=False)
                notas.at[notas.index[-1],'eye_pos']=str(eyes)
                
                #print(notas.tail(1))
                #note end
            else:
                pass
    #remove low duration notes
    indexLowDur = notas[ notas['duracao'] < dur_thresh ].index
    notas=notas.drop(indexLowDur , inplace=False)
    #remove out of tune notes
    for index, row in notas.iterrows():
        i=int(notas.at[index,'i'])
        j=int(notas.at[index,'j'])
        note=int(round(np.average(midi[i:j])))
        std = np.sqrt(np.average(abs(midi[i:j] - note)**2))#std deviation
        #print(np.abs(midi[i:j]-note)<tuneThresh)
        notesThatPassed=np.abs(midi[i:j]-note)<tune_thresh
        if not all(notesThatPassed):
            #remove that line         
            notas=notas.drop(index , inplace=False)
        else:
            notas.at[index,'midi']=note
            notas.at[index,'std dev']=std
    
    print("identifyed notes: ")
    print(notas)
    vName=vName.split('.')[0]
    #notas.to_csv(vName+'.csv', index = False)
    return notas


def folder_note_split(instrument_name=None, threshold=0.8, tune_thresh=0.3,dur_thresh=0.05):
    """
    folder: string containig a folder that contains .mp4 files
    """
    if instrument_name is None:
        instruments= [inst for inst in os.listdir('instruments') if inst[0]!='.']
    else:
        instruments=[instrument_name]

    for instrument in instruments:
        folder=Path('instruments')/Path(instrument)
        videos=[video_path for video_path in folder.iterdir() if video_path.exists() and video_path.suffix=='.mp4']
        dfs=[]
        for vid in videos:
            dfs.append(video_note_split(str(vid), threshold, tune_thresh, dur_thresh))
        df=pd.concat(dfs, keys=videos,names=[folder, 'Notes'])
        df.to_csv(Path(folder)/Path(instrument+'.csv'))
        df=df.reset_index(level=[folder])
    
#notas_flauta=folder_note_split('recorder',threshold=0.8, tune_thresh=0.6,dur_thresh=0.05)
#(notas_flauta['midi'].min(),notas_flauta['midi'].max())
folder_note_split()

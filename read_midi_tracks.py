



from mido import MidiFile
import mido
import time
'''MetaMessage('time_signature', numerator=4, denominator=4, clocks_per_click=24, notated_32nd_notes_per_beat=8, time=0),
    MetaMessage('key_signature', key='A', time=0),
    MetaMessage('set_tempo', tempo=500000, time=0),
    Message('control_change', channel=0, control=121, value=0, time=0),
    Message('program_change', channel=0, program=57, time=0),
    Message('control_change', channel=0, control=7, value=100, time=0),
    Message('control_change', channel=0, control=10, value=64, time=0),
    Message('control_change', channel=0, control=91, value=0, time=0),
    Message('control_change', channel=0, control=93, value=0, time=0),
    MetaMessage('midi_port', port=0, time=0),
    Message('note_on', channel=0, note=54, velocity=80, time=0),
    Message('note_on', channel=0, note=54, velocity=0, time=239),
    Message('note_on', channel=0, note=57, velocity=80, time=241),
    
    Message('note_on', channel=0, note=54, velocity=80, time=0),
    Message('note_on', channel=0, note=54, velocity=0, time=239),
    Message('note_on', channel=0, note=57, velocity=80, time=241),
    Message('note_on', channel=0, note=57, velocity=0, time=239),
    Message('note_on', channel=0, note=61, velocity=80, time=1),
    Message('note_on', channel=0, note=61, velocity=0, time=239),
    Message('note_on', channel=0, note=57, velocity=80, time=241),
    Message('note_on', channel=0, note=57, velocity=0, time=239),
    Message('note_on', channel=0, note=54, velocity=80, time=241),
    Message('note_on', channel=0, note=54, velocity=0, time=239),
    Message('note_on', channel=0, note=50, velocity=80, time=1),
    Message('note_on', channel=0, note=50, velocity=0, time=119),
    Message('note_on', channel=0, note=50, velocity=80, time=121),'''
def read_midi_tracks(filename,track_num=-1,dur_mult=1, transpose=0, verbose=False):
    """
    filename: string .mid
    track_num: number of the track, if 0, return all tracks
    creates and returns a song structure, with midi notes, start time and duration
    note: midi note
    velocity: sound loudness/amplitude/volume
    type 0 (single track): all messages are saved in one track
    type 1 (synchronous): all tracks start at the same time
    type 2 (asynchronous): each track is independent of the others

    """
    song=[]
    mid = MidiFile(filename)
    if verbose:
        print(f"file:{mid.filename}, type:{mid.type}, ticks_per_beat:{mid.ticks_per_beat}, clip:{mid.clip}")
    if mid.type==0 or mid.type==1:
        for i, track in enumerate(mid.tracks):
            print(f'Track {i}: {track.name}')        
            midiNotes=list()#[len(mid.tracks)][]
            startTimes=list()
            endTimes=list() 
            mi=0
            cumulative_time=0.0
            for msg in track:            
                if not msg.is_meta:                
                    if msg.type=='note_on' and msg.velocity!=0:
                        midiNotes.append(msg.note+transpose)
                        startTimes.append(cumulative_time)
                        cumulative_time+=mido.tick2second(msg.time,mid.ticks_per_beat,mido.bpm2tempo(mid.ticks_per_beat))*dur_mult               
                        endTimes.append(cumulative_time)
                        mi+=1
                    else:    
                        cumulative_time+=mido.tick2second(msg.time,mid.ticks_per_beat,mido.bpm2tempo(mid.ticks_per_beat)*dur_mult)                
            song.append({'midi':midiNotes,'start':startTimes,'end':endTimes})
    if track_num==-1:
        print('returning all tracks')
        return song
    else:
        print('returning track '+str(track_num))
        return song[track_num]



notas_musica=read_midi_tracks('bach_badinerie.mid',track_num=-1,dur_mult=2,transpose=7)
for t in notas_musica:
    print(len(t['midi']))
    #print(t)

from pydub import AudioSegment
from pydub.playback import play
from pygame import mixer
from mutagen.wave import WAVE
import time
import math
import wave
import os
import pygame.mixer as mixer
import pygame

#The following is for Streaming, specifically for Sending
def split_audio(start, end, file, export_name):
    start = start * 1000
    end = end * 1000
    newAudio = AudioSegment.from_mp3(file)
    newAudio = newAudio[start:end]
    newAudio.export(export_name + ".wav", format="wav")
 
def get_audio_duration(song):
    audio = WAVE(song)
    audio_info = audio.info
    length = int(audio_info.length)
    return length

#with open("newSong.wav", "rb") as f:
#    wav_data = f.read()   
#byte_data = bytearray(wav_data)
#string_test = byte_data.decode("latin-1")

def audio_streaming(song_path, name):
    length_in_seconds = get_audio_duration(song_path)
    for i in range(math.ceil(length_in_seconds/10)):
        split_audio(i*10, i*10+10, song_path, name+str(i))
        with open(name+str(i)+".wav", "rb") as f:
            wav_data = f.read()    
        byte_data = bytearray(wav_data)
        string_test = byte_data.decode("latin-1")
        #MQTT-Nachricht Einfügen
        #os.remove(name+str(i)+".wav")
        time.sleep(0)
        
        



# The following part is for receifing the Stream

#TODO: Methode schreiben, die Daten bekommt, zu files macht und in playlist einfügt
#evtl beachten, ob es gleicher song ist, wenn nicht alles was in queue ist herausladen
      
#Playing song
def insert_into_playlist(playlist, music_file):
    playlist.append(music_file)
    
def start_playlist(playlist):
    mixer.music.load(playlist[0]) 
    playlist.pop(0)
    mixer.music.play()
    mixer.music.queue(playlist[0])
    playlist.pop(0)
    mixer.music.set_endevent(pygame.USEREVENT+1)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT+1:
                print("finished playing song")
                if len(playlist) > 0:
                    mixer.music.queue(playlist[0])
                    playlist.pop(0)
            if not mixer.music.get_busy():
                running = False
                break

if __name__ == "__main__":
    pygame.init()
    playList = []
    audio_streaming("flask_website/music/Fate.wav", "test")
    time.sleep(1)
    for file in os.listdir():
        if file.endswith(".wav"):
            insert_into_playlist(playList, file)# Am besten sofort, wenn man files bekommt hineinladen ==> sonst evtl falsche reihenfolge
    start_playlist(playList)# Ist Endlosschleife ==> muss behoben werden
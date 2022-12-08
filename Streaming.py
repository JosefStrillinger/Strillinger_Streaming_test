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

playlist = []

#The following is for Streaming, specifically for Sending
def split_audio(start, end, file, export_name):
    start = start * 1000
    end = end * 1000
    newAudio = AudioSegment.from_file(file, ".wav")
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
    first_segment = True
    length_in_seconds = get_audio_duration(song_path)
    for i in range(math.ceil(length_in_seconds/10)):
        split_audio(i*10, i*10+10, song_path, name+str(f"{i:02d}"))  #split_audio(i*10, i*10+10, song_path, name+str(i))
        with open(name+str(f"{i:02d}")+".wav", "rb") as f:
            wav_data = f.read()    
        byte_data = bytearray(wav_data)
        string_data = byte_data.decode("latin-1")
        #MQTT-Nachricht Einfügen
        #os.remove(name+str(f"{i:02d}")+".wav")
        time.sleep(3)
        if(first_segment):
            first_segment = False
            #play schicken
            
        
        



# The following part is for receifing the Stream

#TODO: Methode schreiben, die Daten bekommt, zu files macht und in playlist einfügt
#evtl beachten, ob es gleicher song ist, wenn nicht alles was in queue ist herausladen
      
      
# Maybe make a function, which clears the playlist of old songs
def clear_playlist(playlist):
    pass

# function to clear dir of unneeded songs
def clear_directory(dir_path):
    pass

# Function for turning received string data into wav files, which are later used to play audio     
def receive_songs(string_data, dir_path, name):
    new_bytes = string_data.encode("latin-1")
    count = 0
    for path in os.scandir(dir_path):
        if path.is_file():
            if path.endswith(".wav"):
                count += 1
    song = AudioSegment(new_bytes, sample_width=2, frame_rate=44100, channels=2)
    song.export(dir_path + "/" + name + str(f"{count:02d}") +".wav", format="wav")
    playlist.append(dir_path + "/" + name + str(f"{count:02d}") +".wav")   
      
def receive_song(string_data, dir_path, name):
    new_bytes = string_data.encode("latin-1")
    song = AudioSegment(new_bytes, sample_width=2, frame_rate=44100, channels=2)
    song.export(dir_path + "/" + name +".wav", format="wav")
    playlist.append(dir_path + "/" + name +".wav")   
        
# Change to insert one file into playlist
def insert_all_into_playlist(playlist):
    for file in os.listdir():
        if file.endswith(".wav"):
            #if file not in playlist:
            playlist.append(file)
            print(playlist)
    
def insert_into_playlist(playlist, song_name, dir_path):
    print(song_name)
    

def start_playlist(playlist):
    mixer.music.load(playlist[0]) 
    playlist.pop(0)
    mixer.music.play()
    mixer.music.queue(playlist[0])
    playlist.pop(0)
    MUSIC_END = pygame.USEREVENT+1
    mixer.music.set_endevent(MUSIC_END)
    running = True
    while running:# TODO: playlist ohne while True oder mutlithreading
        for event in pygame.event.get():
            if event.type == MUSIC_END:
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
    help_number = 0
    # Am besten sofort, wenn man files bekommt hineinladen ==> sonst evtl falsche reihenfolge
    insert_all_into_playlist(playList)
    start_playlist(playList)# Ist Endlosschleife ==> muss behoben werden
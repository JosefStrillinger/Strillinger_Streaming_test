from pydub import AudioSegment
from pydub.playback import play
from pygame import mixer
from mutagen.wave import WAVE
import time
import math
import wave
import os

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

with open("newSong.wav", "rb") as f:
    wav_data = f.read()   
byte_data = bytearray(wav_data)
string_test = byte_data.decode("latin-1")

def audio_streaming(song_path, name):
    length_in_seconds = get_audio_duration(song_path)
    for i in range(math.ceil(length_in_seconds/10)):
        split_audio(i*10, i*10+10, song_path, name+str(i))
        with open(name+str(i)+".wav", "rb") as f:
            wav_data = f.read()    
        byte_data = bytearray(wav_data)
        string_test = byte_data.decode("latin-1")
        #MQTT-Nachricht Einfügen
        os.remove(name+str(i)+".wav")
        time.sleep(1)
        
        
audio_streaming("flask_website/music/Fate.wav", "test")
        
        
        
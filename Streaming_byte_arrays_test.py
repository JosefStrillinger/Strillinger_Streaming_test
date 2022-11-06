import os
from pydub import AudioSegment
from pydub.playback import play
from pygame import mixer
import wave
import io
import time
from pathlib import Path
import simpleaudio as sa

music_folder = Path("flask_website/music/")
music_to_play = music_folder / "EverythingBlack.wav"

#with wave.open("flask_website/music/EverythingBlack.wav") as fd:
#   params = fd.getparams()
#   print(fd.getnframes())
#   fd.readframes(1000000)
#   frames = fd.readframes(1000)

def split_audio(start, end, file):
    start = start * 1000
    end = end * 1000
    newAudio = AudioSegment.from_wav(file)
    newAudio = newAudio[start:end]
    newAudio.export("newSong.wav", format="wav")
    
split_audio(0, 10, "flask_website/music/EverythingBlack.wav")

wave_data = wave.open("newSong.wav", "rb")
#wave_data = wave.open("flask_website/music/EverythingBlack.wav", "rb")
bytes_data = wave_data.readframes(-1)

string_test = bytes_data.decode("utf-8")#muss noch überprüft werden, wie man am besten von string zu byte und wieder zurück convertiert

new_bytes = string_test.encode("utf-8")

song = AudioSegment(new_bytes, sample_width=2, frame_rate=44100, channels=2)
song.export("file.wav", format="wav")

wave_obj = sa.WaveObject.from_wave_read(wave_data)

#song.export("file.wav", format="wav")
mixer.init()
mixer.music.load("file.wav")
mixer.music.set_volume(0.5)

def isFloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

while True:
    query = input("INPUT: ")
    if (query == "stop"):
        #play_obj.stop()
        mixer.music.stop()
        break
    elif (query == "play"):
        #play_obj = sa.play_buffer(bytes_data, 2, 2, 44100)
        mixer.music.play()
    elif (query == "pause"):
        mixer.music.pause()
    elif (query == "unpause"):
        mixer.music.unpause()
    elif (isFloat(query)):
        mixer.music.set_volume(float(query))
        print("volume changed")
    else:
        print("sei ned deppat, dua gscheid")
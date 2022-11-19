import os
from pydub import AudioSegment
from pydub.playback import play
from pygame import mixer
import wave
import io
import time
from pathlib import Path
import simpleaudio as sa
import youtube_dl

music_folder = Path("flask_website/music/")
music_to_play = music_folder / "EverythingBlack.wav"

AudioSegment.converter = "D:\\Apps\\ffmpeg-5.1.2-full_build\\ffmpeg-5.1.2-full_build\\bin\\ffmpeg.exe"
AudioSegment.ffprobe = "D:\\Apps\\ffmpeg-5.1.2-full_build\\ffmpeg-5.1.2-full_build\\bin\\ffprobe.exe"

#with wave.open("flask_website/music/EverythingBlack.wav") as fd:
#   params = fd.getparams()
#   print(fd.getnframes())
#   fd.readframes(1000000)
#   frames = fd.readframes(1000)

def split_audio(start, end, file):
    start = start * 1000
    end = end * 1000
    newAudio = AudioSegment.from_mp3(file)
    newAudio = newAudio[start:end]
    newAudio.export("newSong.wav", format="wav")
    
#split_audio(0, 10, "flask_website/music/EverythingBlack.wav")
path_to_fate = Path("D:\\GitHubDirectory\\Strillinger_Streaming_test\\flask_website\\music\\Fate.mp3")
split_audio(0, 10, "flask_website/music/Fate.wav")
#split_audio(0, 30, "flask_website/music/ChildrenOfTheOmnissiah.wav")


wave_data = wave.open("newSong.wav", "rb")
#wave_data = wave.open("flask_website/music/EverythingBlack.wav", "rb")
bytes_data = wave_data.readframes(-1)
#bytes_data = bytearray(wave_data) ==> Funktioniert nicht

with open("newSong.wav", "rb") as f:
    wav_data = f.read()
    
byte_data = bytearray(wav_data)

#f = open("bytes_data.txt", "wb")
#f.write(bytes_data)
#f.close()
#
#f1 = open("str_data.txt", "w")
#f1.write(str(bytes_data))
#f1.close()

#time.sleep(5)

string_test = byte_data.decode("latin-1")

new_bytes = string_test.encode("latin-1")

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
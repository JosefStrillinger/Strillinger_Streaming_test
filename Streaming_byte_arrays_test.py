from pydub import AudioSegment
from pydub.playback import play
import pygame as mixer
import wave
import io

with wave.open("EverythingBlack.wav") as fd:
    params = fd.getparams()
    print(fd.getnframes())
    fd.readframes(1000000)
    frames = fd.readframes(1000) 

wave_data = wave.open("EverythingBlack.wav", "r")
bytes_data = wave_data.readframes(-1)

#print(bytes_data)

#data = open('Audio_test/ChildrenOfTheOmnissiah.mp3', 'rb').read()

#print(data)

# Zwischen den folgenden 2 Möglichkeiten muss entschieden werden ==> testen und bessere Variante wählen
s = io.BytesIO(bytes_data)
song = AudioSegment(bytes_data, sample_width=2, frame_rate=44100, channels=2)
play(song)

sound = mixer.Sound(wave_data)
sound.play()
#song = AudioSegment.from_file(io.BytesIO(bytes_data), format="wav")
#play(song)

#TODO: implement streaming into mqtt ==> check which option for byte conversion is superior
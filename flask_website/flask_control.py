import json
import os
import wave
from flask_restful import Api
#from requests import request
#from model import Question, getRandomQuestion, getData, Service, AllQuests, getQuests
from rest import MusicInfo, Service, getMusicInfo
from flask import Flask, render_template, session, request, url_for, redirect, send_file
from flask_mqtt import Mqtt
from pygame import mixer
import time
import paho.mqtt.client as paho
from paho import mqtt
import time
from pydub import AudioSegment
from mutagen.wave import WAVE
import math
from youtube_downloader import AudioDownloaderYouTube

#
# Copyright 2021 HiveMQ GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)
    #client.publish("pro/music", payload=client._client_id.decode("utf-8") + "-getSongs", qos=1)    #Später wieder aktivieren, wenn getSongs geschrieben, damit man abspielen kann
    

# # with this callback you can see if your publish was successful
# def on_publish(client, userdata, mid, properties=None):
#     print("mid: " + str(mid))

# # print which topic was subscribed to
# def on_subscribe(client, userdata, mid, granted_qos, properties=None):
#     print("Subscribed: " + str(mid) + " " + str(granted_qos))

# print message, useful for checking if it was successful
allSongs = []
neededSongs = []
songsReceived = False
path = "music"
songs_in_dir = []

def on_message(client, userdata, msg):
    neededSongs.clear()
    received = msg.payload.decode("utf-8").split("-");
    if("songs" in received[0]):
        received[1] = received[1].replace("[", "")
        received[1] = received[1].replace("]", "") 
        received[1] = received[1].replace("'", "")      
        received[1] = received[1].replace(".mp3", "")
        allSongs = received[1].split(", ")
        for s in allSongs:
            print(s)
            
            neededSongs.append(s)
            
        songsReceived = True

# using MQTT version 5 here, for 3.1.1: MQTTv311, 3.1: MQTTv31
# userdata is user defined data of any type, updated by user_data_set()
# client_id is the given name of the client

client = paho.Client(client_id="main", userdata=None, protocol=paho.MQTTv5)
client.on_connect = on_connect

client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
client.username_pw_set("project", "wasd1234")

client.connect("cbe265c6cda342daa94ba67720ef1767.s2.eu.hivemq.cloud", 8883, 65535)#3. value ist keepalive


client.on_message = on_message

client.subscribe("pro/music", qos=1)
client.subscribe("pro/status", qos=1)


client.loop_start()
time.sleep(1)
client.loop_stop()
#client.loop_forever()

app = Flask(__name__)
app.secret_key = "sas_diplomarbeit_21/22"
api = Api(app)

#url_for('static', filename='style.css')

def get_songs_in_dir(path):
    global songs_in_dir 
    songs_in_dir = os.listdir(path)

def split_audio(start, end, file, export_name):
    start = start * 1000
    end = end * 1000
    newAudio = AudioSegment.from_file(file)
    newAudio = newAudio[start:end]
    newAudio.export(export_name, format="wav")
 
def get_audio_duration(song):
    audio = WAVE(song)
    audio_info = audio.info
    length = int(audio_info.length)
    return length

# The following is for sending the audio data as a string through mqtt
#client.loop_start()
#client.publish("pro/music", payload = client._client_id.decode("utf-8") + "-play-" + in_string, qos=1)
#client.loop_stop()

def audio_streaming(song_path, name):# Einfügen, dass sobald stop gedrückt ist, nichts mehr gesendet wird (bool variable should_send)
    first_segment = True
    length_in_seconds = get_audio_duration(song_path)
    for i in range(math.ceil(length_in_seconds/10)):
        split_audio(i*10, i*10+10, song_path, name+str(f"{i:02d}")+".wav")  #split_audio(i*10, i*10+10, song_path, name+str(i))
        with open(name+str(f"{i:02d}") + ".wav" , "rb") as f:
            wav_data = f.read()    
        byte_data = bytearray(wav_data)
        string_data = byte_data.decode("latin-1")
        #MQTT-Nachricht Einfügen
        client.loop_start()
        client.publish("pro/music", payload = client._client_id.decode("utf-8") + "-song-" + name+str(f"{i:02d}") + "-" + string_data, qos=1)
        client.loop_stop()
        os.remove(name+str(f"{i:02d}")+".wav")
        time.sleep(4)
        if(first_segment):
            client.loop_start()
            client.publish("pro/music", payload = client._client_id.decode("utf-8") + "-play", qos=1)
            client.loop_stop()
            print("play")
            time.sleep(1)
            first_segment = False

@app.route('/')
def start():
    return render_template("startseite.html")

@app.route('/download')
def download():
    return render_template("download.html")

@app.route('/account')
def account():
    #TODO: add functionality to account, not needed right now, maybe later
    return render_template("account.html")


@app.route('/data')
def data():
    #TODO: data vizualisation
    
    return render_template("data.html")

@app.route('/download_song', methods=['GET', 'POST'])
def download_song():
    link_to_song = request.form.get("link")
    ady = AudioDownloaderYouTube([link_to_song])
    ady.set_params(path, "wav")
    ady.download()
    return redirect(url_for("download"))
    
@app.route('/songs')
def showSongs():
    #client.loop_start()
    #client.publish("pro/music", payload=client._client_id.decode("utf-8") + "-getSongs", qos=1)
    #time.sleep(1)
    #client.loop_stop()
    global songs_in_dir 
    songs_in_dir = os.listdir(path)
    return render_template("songs.html", songs = getMusicInfo(songs_in_dir))

@app.route('/play')
@app.route('/play/<name>', methods=['GET', 'POST'])
def play(name):
    global songs_in_dir
    get_songs_in_dir(path)
    print(name)
    time.sleep(0.01)
    #Funktion für Streaming: 
    help = name.split(".")
    audio_streaming(path+"/"+name, help[0]) # TODO: Receive für Raspberry schreiben
    #return render_template("songs.html", songs=getMusicInfo(songs_in_dir))
    return redirect(url_for("showSongs"))

@app.route('/stop', methods=['GET', 'POST'])
def stop():
    global songs_in_dir
    get_songs_in_dir(path)
    client.loop_start()
    client.publish("pro/status", payload = client._client_id.decode("utf-8") + "-stop", qos=1)
    time.sleep(0)
    client.publish("pro/music", payload = client._client_id.decode("utf-8") + "-" + "stop", qos=1)
    #time.sleep(1)
    client.loop_stop()
    time.sleep(0.1)
    #mixer.music.stop()
    #return render_template("songs.html", songs=getMusicInfo(songs_in_dir))
    return redirect(url_for("showSongs"))

@app.route('/pause', methods=['GET', 'POST'])
def pause():
    global songs_in_dir
    get_songs_in_dir(path)
    client.loop_start()
    client.publish("pro/status", payload = client._client_id.decode("utf-8") + "-pause", qos=1)
    time.sleep(0)
    client.publish("pro/music", payload = client._client_id.decode("utf-8") + "-" + "pause", qos=1)
    client.loop_stop()
    time.sleep(0.1)
    #mixer.music.pause()
    #return render_template("songs.html", songs=getMusicInfo(songs_in_dir))
    return redirect(url_for("showSongs"))

@app.route('/unpause', methods=['GET', 'POST'])
def unpause():
    global songs_in_dir
    get_songs_in_dir(path)
    client.loop_start()
    client.publish("pro/status", payload = client._client_id.decode("utf-8") + "-unpause", qos=1)
    time.sleep(0)
    client.publish("pro/music", payload = client._client_id.decode("utf-8") + "-" + "unpause", qos=1)
    client.loop_stop()
    time.sleep(0.1)
    #mixer.music.unpause()
    #return render_template("songs.html", songs=getMusicInfo(songs_in_dir))
    return redirect(url_for("showSongs"))

@app.route('/volume')
@app.route('/volume', methods=['GET', 'POST'])
def volume():
    volume = request.form.get('volume')
    global songs_in_dir
    get_songs_in_dir(path)
    #volume=request.args["rangeval"]
    print(volume)
    val = float(volume)
    valPyGame = val/100
    client.loop_start() 
    client.publish("pro/status", payload = client._client_id.decode("utf-8") + "-volumne", qos=1)
    time.sleep(0)
    client.publish("pro/music", payload = client._client_id.decode("utf-8") + "-"+str(valPyGame), qos=1)
    client.loop_stop()
    time.sleep(1)
    print(valPyGame)
    #return render_template("songs.html", songs = getMusicInfo(songs_in_dir))
    return redirect(url_for("showSongs"))

#TODO: 

api.add_resource(Service, "/rest/<int:id>")

if __name__ == '__main__':
    app.debug = True
    app.run()
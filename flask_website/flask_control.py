import json
import os
import wave
from flask_restful import Api
from requests import request
#from model import Question, getRandomQuestion, getData, Service, AllQuests, getQuests
from rest import MusicInfo, Service, getMusicInfo
from flask import Flask, render_template, session, request, url_for
from pygame import mixer
import time
import paho.mqtt.client as paho
from paho import mqtt
import time
from pydub import AudioSegment

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
        #runInputs(songsReceived, allSongs)
# def on_log(client,userdata,level,buff):
#     print(buff)  

# using MQTT version 5 here, for 3.1.1: MQTTv311, 3.1: MQTTv31
# userdata is user defined data of any type, updated by user_data_set()
# client_id is the given name of the client
client = paho.Client(client_id="main", userdata=None, protocol=paho.MQTTv5)
client.on_connect = on_connect

# enable TLS for secure connection
client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
# set username and password
client.username_pw_set("project", "wasd1234")
# connect to HiveMQ Cloud on port 8883 (default for MQTT)
client.connect("cbe265c6cda342daa94ba67720ef1767.s2.eu.hivemq.cloud", 8883)

# setting callbacks, use separate functions like above for better visibility
# client.on_subscribe = on_subscribe
client.on_message = on_message
# client.on_publish = on_publish
# client.on_log = on_log

# subscribe to all topics of encyclopedia by using the wildcard "#"
client.subscribe("pro/music", qos=1)
# a single publish, this can also be done in loops, etc.

#client.publish("pro/music", payload=client._client_id.decode("utf-8") + "-play-Everything_Black.mp3", qos=1)

client.loop_start()
time.sleep(1)
client.loop_stop()
#client.loop_forever()

app = Flask(__name__)
app.secret_key = "epjsmp2021/22"
api = Api(app)


#url_for('static', filename='style.css')

@app.route('/')
def start():
    return render_template("startseite.html")

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
@app.route('/play/<name>')
def play(name):
    global songs_in_dir
    print(name)
    split_audio(0, 20, path + "/" + name, "r")
    #wave_data = wave.open(path + "/" + name, "r")
    wave_data = wave.open("newSong.wav")
    bytes_data = wave_data.readframes(-1)
    client.loop_start()
    client.publish("pro/music", payload = client._client_id.decode("utf-8") + "-play-" + str(bytes_data), qos=1)
    client.loop_stop()
    time.sleep(0.1)
    return render_template("songs.html", songs=getMusicInfo(songs_in_dir))

def split_audio(start, end, file):
    start = start * 1000
    end = end * 1000
    newAudio = AudioSegment.from_wav(file)
    newAudio = newAudio[start:end]
    newAudio.export("newSong.wav", format="wav")
    

@app.route('/stop')
def stop():
    client.loop_start()
    client.publish("pro/music", payload = client._client_id.decode("utf-8") + "-" + "stop", qos=1)
    #time.sleep(1)
    client.loop_stop()
    time.sleep(0.1)
    #mixer.music.stop()
    return render_template("songs.html", songs=getMusicInfo(songs_in_dir))

@app.route('/pause')
def pause():
    client.loop_start()
    client.publish("pro/music", payload = client._client_id.decode("utf-8") + "-" + "pause", qos=1)
    client.loop_stop()
    time.sleep(0.1)
    #mixer.music.pause()
    return render_template("songs.html", songs=getMusicInfo(songs_in_dir))

@app.route('/unpause')
def unpause():
    client.loop_start()
    client.publish("pro/music", payload = client._client_id.decode("utf-8") + "-" + "unpause", qos=1)
    client.loop_stop()
    time.sleep(0.1)
    #mixer.music.unpause()
    return render_template("songs.html", songs=getMusicInfo(songs_in_dir))  

@app.route('/volume')
@app.route('/volume/<volume>')
def volume(volume):
    #volume=request.args["rangeval"]
    print(volume)
    val = float(volume)
    valPyGame = val/100
    client.loop_start() 
    client.publish("pro/music", payload = client._client_id.decode("utf-8") + "-"+str(valPyGame), qos=1)
    client.loop_stop()
    time.sleep(1)
    print(valPyGame)
    return render_template("songs.html", songs = getMusicInfo(songs_in_dir))

#TODO: Sound ändern einfügen

api.add_resource(Service, "/rest/<int:id>")

if __name__ == '__main__':
    app.debug = True
    app.run()
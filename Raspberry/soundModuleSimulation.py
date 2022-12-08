from ctypes import sizeof
import os
import time
from tokenize import Double
from unicodedata import decimal
from urllib.parse import urlparse
import paho.mqtt.client as paho
from paho import mqtt
from pygame import mixer
from pydub import AudioSegment
import pygame

directory = "Sound/"

def isFloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

box_name = "raspi_test"
loggedIn = False
playlist = []

def on_connect(client, userdata, flags, rc, properties=None):
    #("CONNACK received with code %s." % rc)
    pygame.init()
    mixer.init()
    mixer.music.set_volume(0.1)

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

def insert_into_playlist(dir_path, playlist):
    for file in os.listdir(dir_path):
        if file.endswith(".wav"):
            if file not in playlist:
                playlist.append(file)

def receive_song(string_data, dir_path, name):
    new_bytes = string_data.encode("latin-1")
    song = AudioSegment(new_bytes, sample_width=2, frame_rate=44100, channels=2)
    song.export(dir_path + "/" + name +".wav", format="wav")
    playlist.append(dir_path + "/" + name +".wav")   
    
def start_playlist():
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

# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    global box_name, loggedIn
    received = msg.payload.decode("utf-8").split("-", 3)
    #print(received)
    #print(received)
    if(received[0] == "server" and "=>" in received[1] and loggedIn == False):
        box_name = received[1].replace("=>", "")
        print("Logged in as " + str(box_name))
        loggedIn = True
    if(received[0] != box_name): #and loggedIn == True):
        if received[1] == "raspi_test":
            client.publish("pro/status", payload=client._client_id.decode("utf-8") + "-" + "Online", qos=1)
            print("Still running")
        else:    
            if(received[1] == "play"):
                #new_bytes = received[3].encode("latin-1")
                #song = AudioSegment(new_bytes, sample_width=2, frame_rate=44100, channels=2)# Idee, schreiben wieso man diese Argumente braucht
                #song.export("file.wav", format="wav")
                
                pass
                #start_playlist()
                #print(received[0] + ": " + received[1] + ", " + received[2])
            else:
                if(received[1] == "song" and received[3] != None):
                    receive_song(received[3], "Raspberry/received_samples", received[2])
                    #start_playlist()
                    #path = "Sound/"
                    #dir_list = os.listdir(path)
                    #print(str(dir_list))
                    #client.publish("pro/music", payload=client._client_id.decode("utf-8") + "-" + str(dir_list), qos=1)
                elif(received[1] == "stop"):
                    mixer.music.stop()
                elif(received[1] == "play"):
                    mixer.music.play()
                elif(received[1] == "pause"):
                    mixer.music.pause()
                elif(received[1] == "unpause"):
                    mixer.music.unpause()
                elif(isFloat(received[1])):
                    mixer.music.set_volume(float(received[1]))
                #print(received[0] + ": " + received[1])
                #client.publish("pro/music", payload=client._client_id.decode("utf-8") + "-received", qos=1)
                
client = paho.Client(client_id="raspi", userdata=None, protocol=paho.MQTTv5)

client.on_connect = on_connect

# enable TLS for secure connection
client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
# set username and password
client.username_pw_set("project", "wasd1234")
# connect to HiveMQ Cloud on port 8883 (default for MQTT)
client.connect("cbe265c6cda342daa94ba67720ef1767.s2.eu.hivemq.cloud", 8883)

client.on_message = on_message

# subscribe to all topics of encyclopedia by using the wildcard "#"
client.subscribe("pro/music", qos=1)

#client.subscribe("pro/status", qos=1)

def loginBox():
    global client
    client.loop_start()
    client.publish("pro/status", payload=client._client_id.decode("utf-8") + "-Login")
    time.sleep(1)
    client.loop_stop()
    
    client = paho.Client(client_id=box_name, userdata=None, protocol=paho.MQTTv5)
    client.on_connect = on_connect

    # enable TLS for secure connection
    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    # set username and password
    client.username_pw_set("project", "wasd1234")
    # connect to HiveMQ Cloud on port 8883 (default for MQTT)
    client.connect("cbe265c6cda342daa94ba67720ef1767.s2.eu.hivemq.cloud", 8883)##

    client.on_message = on_message

    # subscribe to all topics of encyclopedia by using the wildcard "#"
    client.subscribe("pro/music", qos=1)

    client.subscribe("pro/status", qos=1)

# setting callbacks for different events to see if it works, print the message etc.

#loginBox()

path = "Sound/"
#dir_list = os.listdir(path)
#print(str(dir_list))

client.loop_forever()
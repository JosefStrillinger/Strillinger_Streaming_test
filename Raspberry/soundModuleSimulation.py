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
import threading
import multiprocessing as mp
import pickle
import json

directory = "Sound/"

def isFloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

box_name = "raspi_test"
loggedIn = False


def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)
    

def write_list(list):
    with open('Raspberry/save.json', 'w') as fp:
        json.dump(list, fp)
        print("saving done")

def read_list():
    with open('Raspberry/save.json', 'rb') as fp:
        list = json.load(fp)
        return list 

def receive_songs(string_data, dir_path, name): # Old version, now count is already done by audio_streaming in flask_control
    shared_playlist = read_list()
    new_bytes = string_data.encode("latin-1")
    count = 0
    for path in os.scandir(dir_path):
        if path.is_file():
            if path.endswith(".wav"):
                count += 1
    song = AudioSegment(new_bytes, sample_width=2, frame_rate=44100, channels=2)
    song.export(dir_path + "/" + name + str(f"{count:02d}") +".wav", format="wav")
    shared_playlist.append(dir_path + "/" + name + str(f"{count:02d}") +".wav") 
    print(shared_playlist)

def insert_into_playlist(dir_path, playlist):
    for file in os.listdir(dir_path):
        if file.endswith(".wav"):
            if file not in playlist:
                playlist.append(file)

def receive_song(string_data, dir_path, name):
    shared_playlist = read_list()
    new_bytes = string_data.encode("latin-1")
    song = AudioSegment(new_bytes, sample_width=2, frame_rate=44100, channels=2)
    song.export(dir_path + "/" + name +".wav", format="wav")
    shared_playlist.append(dir_path + "/" + name +".wav")
    write_list(shared_playlist)
    print(len(shared_playlist))   
    
def start_playlist(pause_event, stop_event, unpause_event, volume_event, volume_value):
    pygame.init()
    mixer.init()
    mixer.music.set_volume(0.5)
    count = 0
    shared_playlist = read_list()
    print(shared_playlist)
    mixer.music.load(shared_playlist[count])
    mixer.music.play()
    mixer.music.set_endevent(pygame.USEREVENT+1)
    running = True
    while running:
        if pause_event.is_set():
            mixer.music.pause()
            pause_event.clear()
            print("paused")
        if unpause_event.is_set():
            mixer.music.unpause()
            unpause_event.clear()
            print("unpaused")
        if volume_event.is_set():
            mixer.music.set_volume(volume_value.value)
            volume_event.clear()
            print("volume changed")
        if stop_event.is_set():
            mixer.music.stop()
            stop_event.clear()
            print("stopped")
            delete_old_resources()
            reset_saves()
            break
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT+1:
                print("finished playing song: "+ shared_playlist[count])
                count +=1
                shared_playlist = read_list() 
                #mixer.music.load(shared_playlist[count])
                #mixer.music.play()
                if len(shared_playlist) > count:
                    mixer.music.load(shared_playlist[count])
                    mixer.music.play()
                    #mixer.music.queue(shared_playlist[count])
                    #os.remove(shared_playlist[0])
                    #shared_playlist.pop(0)
                    #write_list(shared_playlist)
                else:
                    if not mixer.music.get_busy():
                        running = False
                        mixer.music.unload()
                        delete_old_resources()
                        reset_saves()
                        break

def reset_saves():
    shared_playlist = read_list()
    print(shared_playlist)
    new_sl = []
    write_list(new_sl)

def delete_old_resources():
    shared_playlist = read_list()
    for i in shared_playlist:
        os.remove(i)
    print("finished")

# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    global box_name, loggedIn
    received = msg.payload.decode("utf-8").split("-", 3)
    print(received[:2])
    #print(received[1])
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
 
                #thread_play = threading.Thread(target=start_playlist)
                #thread_play.start()
                #proc_play = mp.Process(target=start_playlist)
                proc_play.start()
                #proc_play.join()
                print("started play thread")
                #print(threading.currentThread())
                #print(threading.active_count())
                #pass
                #start_playlist()
                #print(received[0] + ": " + received[1] + ", " + received[2])
            else:
                if(received[1] == "song" and received[3] != None):
                    #thread_get = threading.Thread(target=receive_song, args=(received[3], "Raspberry/received_samples", received[2]))
                    #thread_get.start()
                    proc_get = mp.Process(target=receive_song, args=(received[3], "Raspberry/received_samples", received[2], ))
                    proc_get.start()
                    #receive_song(received[3], "Raspberry/received_samples", received[2])
                    print(received[2])
                    #start_playlist()
                    #path = "Sound/"
                    #dir_list = os.listdir(path)
                    #print(str(dir_list))
                    #client.publish("pro/music", payload=client._client_id.decode("utf-8") + "-" + str(dir_list), qos=1)
                elif(received[1] == "stop"):
                    stop_event.set()
                    mixer.music.stop()
                    print("stop")
                elif(received[1] == "pause"):
                    pause_event.set()
                    mixer.music.pause()
                    print("pause")
                elif(received[1] == "unpause"):
                    unpause_event.set()
                    mixer.music.unpause()
                    print("unpause")
                elif(isFloat(received[1])):
                    
                    volume_value.value = float(received[1])
                    volume_event.set()
                    mixer.music.set_volume(float(received[1]))
                #print(received[0] + ": " + received[1])
                #client.publish("pro/music", payload=client._client_id.decode("utf-8") + "-received", qos=1)

def initClient():        
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
    print("Client initialized!")
    return client

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
#client.loop_forever()


if __name__ == "__main__":
    #manager = mp.Manager()
    #shared_playlist = manager.list()
    delete_old_resources()
    reset_saves()
    c = initClient()
    pygame.init()
    mixer.init()
    mixer.music.set_volume(0.5)
    pause_event = mp.Event()
    stop_event = mp.Event()
    unpause_event = mp.Event()
    volume_value = mp.Value('d', 0.0)
    volume_event = mp.Event()
    proc_play = mp.Process(target=start_playlist, args=(pause_event, stop_event, unpause_event, volume_event, volume_value))
    c.loop_forever()
    
    #mp.freeze_support()
    
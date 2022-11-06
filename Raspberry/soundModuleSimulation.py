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
    #("CONNACK received with code %s." % rc)
    mixer.init()
    mixer.music.set_volume(0.1)

# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    global box_name, loggedIn
    received = msg.payload.decode("utf-8").split("-")
    print(received)
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
            if(received[1] == "play" and received[2] != None):
                #song = directory + received[2]
                #print(str(song) + " is loaded")
                bytes_data = bytearray(received[2].encode("utf-8"))
                song = AudioSegment(bytes_data, sample_width=2, frame_rate=44100, channels=2)
                song.export("file.wav", format="wav")
                mixer.music.load("file.wav")
                mixer.music.play()
                print(received[0] + ": " + received[1] + ", " + received[2])
            else:
                if(received[1] == "getSongs"):
                    pass
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
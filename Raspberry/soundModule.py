from ctypes import sizeof
from msilib.schema import PublishComponent
import os
from urllib.parse import urlparse
import paho.mqtt.client as paho
from paho import mqtt
from pygame import mixer

directory = "/home/pi/Music/"

def isFloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    #("CONNACK received with code %s." % rc)
    mixer.init()
    mixer.music.set_volume(0.1)

# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    received = msg.payload.decode("utf-8").split("-");
    if(received[0] != "raspi"):
        if(len(received) == 3):
            song = directory + received[2]
            mixer.music.load(song)
            mixer.music.play()
            print(received[0] + ": " + received[1] + ", " + received[2])
        else:
            if(received[1] == "getSongs"):
                path = "/home/pi/Music/"
                dir_list = os.listdir(path)
                print(str(dir_list))
                client.publish("pro/music", payload=client._client_id.decode("utf-8") + "-" + str(dir_list), qos=1)
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
            print(received[0] + ": " + received[1])
            client.publish("pro/music", payload=client._client_id.decode("utf-8") + "-received", qos=1)

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

path = "/home/pi/Music/"
dir_list = os.listdir(path)
print(str(dir_list))

client.loop_forever()

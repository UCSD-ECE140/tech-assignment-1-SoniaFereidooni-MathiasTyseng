import random
import time

import paho.mqtt.client as paho
from paho import mqtt


# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    """
        Prints the result of the connection with a reasoncode to stdout ( used as callback for connect )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param flags: these are response flags sent by the broker
        :param rc: stands for reasonCode, which is a code for the connection result
        :param properties: can be used in MQTTv5, but is optional
    """
    print("CONNACK received with code %s." % rc)




# with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
    """
        Prints mid to stdout to reassure a successful publish ( used as callback for publish )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param mid: variable returned from the corresponding publish() call, to allow outgoing messages to be tracked
        :param properties: can be used in MQTTv5, but is optional
    """
    print("mid: " + str(mid))




# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    """
        Prints a reassurance for successfully subscribing
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param mid: variable returned from the corresponding publish() call, to allow outgoing messages to be tracked
        :param granted_qos: this is the qos that you declare when subscribing, use the same one for publishing
        :param properties: can be used in MQTTv5, but is optional
    """
    print("Subscribed: " + str(mid) + " " + str(granted_qos))




# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    """
        Prints a mqtt message to stdout ( used as callback for subscribe )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param msg: the message with topic and payload
    """
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))



client1 = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="", userdata=None, protocol=paho.MQTTv5)
client1.on_connect = on_connect


# enable TLS for secure connection
client1.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
# set username and password
client1.username_pw_set("sfereidooni", "CoolKid140")
# connect to HiveMQ Cloud on port 8883 (default for MQTT)
client1.connect("6e55730bd5364136b3eea32f4fcb7183.s1.eu.hivemq.cloud", 8883)


client1.on_publish = on_publish

client2 = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="", userdata=None, protocol=paho.MQTTv5)
client2.on_connect = on_connect


# enable TLS for secure connection
client2.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
# set username and password
client2.username_pw_set("sfereidooni", "CoolKid140")
# connect to HiveMQ Cloud on port 8883 (default for MQTT)
client2.connect("6e55730bd5364136b3eea32f4fcb7183.s1.eu.hivemq.cloud", 8883)


client2.on_publish = on_publish

client_sub = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="", userdata=None, protocol=paho.MQTTv5)
client_sub.on_connect = on_connect


# enable TLS for secure connection
client_sub.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
# set username and password
client_sub.username_pw_set("sfereidooni", "CoolKid140")
# connect to HiveMQ Cloud on port 8883 (default for MQTT)
client_sub.connect("6e55730bd5364136b3eea32f4fcb7183.s1.eu.hivemq.cloud", 8883)


client_sub.on_message = on_message
client_sub.on_publish = on_publish


# subscribe to all topics of numbers by using the wildcard "#"
client_sub.subscribe("numbers/#", qos=1)

client_sub.loop_start()

while(True):
    num1 = random.randint(0,100)
    num2 = random.randint(100,1000)

    client1.publish("numbers/under100", payload=num1, qos=1)
    client2.publish("numbers/over100", payload=num2, qos=1)
    time.sleep(3)
    

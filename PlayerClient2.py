import os
import json
from dotenv import load_dotenv

import paho.mqtt.client as paho
from paho import mqtt
import time

curr_position_1 = None
curr_position_2 = None
curr_position_3 = None
curr_position_4 = None

# prev_1 = None
# prev_2 = None
# prev_3 = None
# prev_4 = None

explored = []

p1_frontier = []
p2_frontier = []
p3_frontier = []
p4_frontier = []

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

    print("message: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

    player_number = 0

    if "Player" in msg.topic:
        player_number = int(msg.topic[22:23])

    if player_number == 1:
        curr_position_1 = json.loads(msg.payload.decode('utf-8'))["currentPosition"]
        print("IT CHANGED ",curr_position_1)
        p1_frontier.append(curr_position_1)
    if player_number == 2:
        curr_position_2 = json.loads(msg.payload.decode('utf-8'))["currentPosition"]
        p2_frontier.append(curr_position_2)
    if player_number == 3:
        curr_position_3 = json.loads(msg.payload.decode('utf-8'))["currentPosition"]
        p3_frontier.append(curr_position_3)
    if player_number == 4:
        curr_position_4 = json.loads(msg.payload.decode('utf-8'))["currentPosition"]
        p4_frontier.append(curr_position_4)

    print("first frontier", p1_frontier)

if __name__ == '__main__':
    load_dotenv(dotenv_path='./credentials.env')
    
    broker_address = os.environ.get('BROKER_ADDRESS')
    broker_port = int(os.environ.get('BROKER_PORT'))
    username = os.environ.get('USER_NAME')
    password = os.environ.get('PASSWORD')

    client = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="Player1", userdata=None, protocol=paho.MQTTv5)
    
    # enable TLS for secure connection
    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    # set username and password
    client.username_pw_set(username, password)
    # connect to HiveMQ Cloud on port 8883 (default for MQTT)
    client.connect(broker_address, broker_port)

    # setting callbacks, use separate functions like above for better visibility
    client.on_subscribe = on_subscribe # Can comment out to not print when subscribing to new topics
    client.on_message = on_message
    client.on_publish = on_publish # Can comment out to not print when publishing to topics

    lobby_name = "TestLobby"
    player_1 = "Player1"
    player_2 = "Player2"
    player_3 = "Player3"
    player_4 = "Player4"

    client.subscribe(f"games/{lobby_name}/lobby")
    client.subscribe(f'games/{lobby_name}/+/game_state')
    client.subscribe(f'games/{lobby_name}/scores')

    client.publish("new_game", json.dumps({'lobby_name':lobby_name,
                                            'team_name':'ATeam',
                                            'player_name' : player_1}))
    
    client.publish("new_game", json.dumps({'lobby_name':lobby_name,
                                            'team_name':'ATeam',
                                            'player_name' : player_2}))
    
    client.publish("new_game", json.dumps({'lobby_name':lobby_name,
                                        'team_name':'BTeam',
                                        'player_name' : player_3}))
    
    client.publish("new_game", json.dumps({'lobby_name':lobby_name,
                                        'team_name':'BTeam',
                                        'player_name' : player_4}))

    time.sleep(1) # Wait a second to resolve game start

    client.publish(f"games/{lobby_name}/start", "START")

    client.loop_start()

    time.sleep(3)

    #onchange
    while(len(p1_frontier) != 0 and len(p2_frontier) != 0 and len(p3_frontier) != 0 and len(p4_frontier) != 0):
        moves = ["UP", "RIGHT", "DOWN", "LEFT"]
        move_coords = [(0,1), (1,0), (0,-1), (-1,0)] 

        # prev_current_1 = curr_position_1
        # prev_current_2 = curr_position_2
        # prev_current_3 = curr_position_3
        # prev_current_4 = curr_position_4

        # print("CURR POSITION 1", curr_position_1)
        # print("PREV CURR 1", prev_current_1)

        current_1 = p1_frontier.pop(0)
        current_2 = p2_frontier.pop(0)
        current_3 = p3_frontier.pop(0)
        current_4 = p4_frontier.pop(0)

        prev_current_1 = current_1
        prev_current_2 = current_2
        prev_current_3 = current_3
        prev_current_4 = current_4

        explored.append(current_1)
        explored.append(current_2)
        explored.append(current_3)
        explored.append(current_4)

        #also add a stop once all coins have been collected

        #fill this in later to add children/moves
        neighbors_1 = [(current_1[0]+m[0], current_1[1]+m[1]) for m in move_coords]
        neighbors_2 = [(current_2[0]+m[0], current_2[1]+m[1]) for m in move_coords]
        neighbors_3 = [(current_3[0]+m[0], current_3[1]+m[1]) for m in move_coords]
        neighbors_4 = [(current_4[0]+m[0], current_4[1]+m[1]) for m in move_coords]

        print(neighbors_1)

        for n in neighbors_1:
            if n not in explored and n not in p1_frontier: #also check if in range of grid?
                p1_frontier.append(n)
                
        for n in neighbors_2:
            if n not in explored and n not in p2_frontier: #also check if in range of grid?
                p2_frontier.append(n)
        
        for n in neighbors_3:
            if n not in explored and n not in p3_frontier: #also check if in range of grid?
                p3_frontier.append(n)
                   
        for n in neighbors_4:
            if n not in explored and n not in p4_frontier: #also check if in range of grid?
                p4_frontier.append(n)
                
        #check if in explored loop etc. 

        # p1_frontier = [curr_position_1]
        # p2_frontier = [curr_position_2]
        # p3_frontier = [curr_position_3]
        # p4_frontier = [curr_position_4]

        print("second frontier", p1_frontier)

        print("PREV CURR 1", prev_current_1)

        if (prev_current_1[0]+0, prev_current_1[1]+1) == current_1:
            p1_move = "UP"
        if (prev_current_1[0]+1, prev_current_1[1]+0) == current_1:
            p1_move = "RIGHT"
        if (prev_current_1[0]+0, prev_current_1[1]-1) == current_1:
            p1_move = "DOWN"
        if (prev_current_1[0]-1, prev_current_1[1]+0) == current_1:
            p1_move = "LEFT"

        if (prev_current_2[0]+0, prev_current_2[1]+1) == current_2:
            p2_move = "UP"
        if (prev_current_2[0]+1, prev_current_2[1]+0) == current_2:
            p2_move = "RIGHT"
        if (prev_current_2[0]+0, prev_current_2[1]-1) == current_2:
            p2_move = "DOWN"
        if (prev_current_2[0]-1, prev_current_2[1]+0) == current_2:
            p2_move = "LEFT"

        if (prev_current_3[0]+0, prev_current_3[1]+1) == current_3:
            p3_move = "UP"
        if (prev_current_3[0]+1, prev_current_3[1]+0) == current_3:
            p3_move = "RIGHT"
        if (prev_current_3[0]+0, prev_current_3[1]-1) == current_3:
            p3_move = "DOWN"
        if (prev_current_3[0]-1, prev_current_3[1]+0) == current_3:
            p3_move = "LEFT"

        if (prev_current_4[0]+0, prev_current_4[1]+1) == current_4:
            p4_move = "UP"
        if (prev_current_4[0]+1, prev_current_4[1]+0) == current_4:
            p4_move = "RIGHT"
        if (prev_current_4[0]+0, prev_current_4[1]-1) == current_4:
            p4_move = "DOWN"
        if (prev_current_4[0]-1, prev_current_4[1]+0) == current_4:
            p4_move = "LEFT"

        # p1_move = input("Player 1, make your move: ")
        # p2_move = input("Player 2, make your move: ")
        # p3_move = input("Player 3, make your move: ")
        # p4_move = input("Player 4, make your move: ")

        client.publish(f"games/{lobby_name}/{player_1}/move", p1_move)
        client.publish(f"games/{lobby_name}/{player_2}/move", p2_move)
        client.publish(f"games/{lobby_name}/{player_3}/move", p3_move)
        client.publish(f"games/{lobby_name}/{player_4}/move", p4_move)

        time.sleep(3)

    client.publish(f"games/{lobby_name}/start", "STOP")


    client.loop_forever()

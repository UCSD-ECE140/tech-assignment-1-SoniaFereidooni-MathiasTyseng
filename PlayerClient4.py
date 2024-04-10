import os
import json
from dotenv import load_dotenv

import paho.mqtt.client as paho
from paho import mqtt
import time

currentPosition_p1 = []
currentPosition_p2 = []
currentPosition_p3 = []
currentPosition_p4 = []
coin1 = None
coin2 = None
coin3 = None
walls = []
enemyPositions = None
teammatePositions = None


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

    if ("Player1" in msg.topic):
        currentPosition_p1.append(json.loads(msg.payload).get("currentPosition"))

    if ("Player2" in msg.topic):
        currentPosition_p2.append(json.loads(msg.payload).get("currentPosition"))

    if ("Player3" in msg.topic):
        currentPosition_p3.append(json.loads(msg.payload).get("currentPosition"))
    
    if ("Player4" in msg.topic):
        currentPosition_p4.append(json.loads(msg.payload).get("currentPosition"))
    
    
    # coin1 = json.loads(msg.payload).get("coin1")
    # coin2 = json.loads(msg.payload).get("coin2")
    # coin3 = json.loads(msg.payload).get("coin3")

    walls_vals = json.loads(msg.payload).get("walls")

    if walls_vals:
        for wall in walls_vals:
            if(wall not in walls):
                walls.append(wall)

    # walls.append(json.loads(msg.payload).get("walls"))
    
    enemyPositions = json.loads(msg.payload).get("enemyPositions")

    teammatePositions = json.loads(msg.payload).get("teammatePositions")


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
    # client.publish(f"games/{lobby_name}/start", "START")
    # client.publish(f"games/{lobby_name}/{player_1}/move", "UP")
    # client.publish(f"games/{lobby_name}/{player_2}/move", "DOWN")
    # client.publish(f"games/{lobby_name}/{player_3}/move", "DOWN")
    # client.publish(f"games/{lobby_name}/start", "STOP")

    client.publish(f"games/{lobby_name}/start", "START")

    client.loop_start()

    time.sleep(3)

    explored = []

    #onchange
    while(True):
        curr_pos_p1 = currentPosition_p1[-1]
        curr_pos_p2 = currentPosition_p2[-1]
        curr_pos_p3 = currentPosition_p3[-1]
        curr_pos_p4 = currentPosition_p4[-1]

        # player 1 possible positions

        up_pos_p1_x = int(curr_pos_p1[0])-1
        up_pos_p1_y = int(curr_pos_p1[1])
        up_pos_p1 = [up_pos_p1_x, up_pos_p1_y]

        down_pos_p1_x = int(curr_pos_p1[0])+1
        down_pos_p1_y = int(curr_pos_p1[1])
        down_pos_p1 = [down_pos_p1_x, down_pos_p1_y]

        right_pos_p1_x = int(curr_pos_p1[0])
        right_pos_p1_y = int(curr_pos_p1[1])+1
        right_pos_p1 = [right_pos_p1_x, right_pos_p1_y]

        left_pos_p1_x = int(curr_pos_p1[0])
        left_pos_p1_y = int(curr_pos_p1[1])-1
        left_pos_p1 = [left_pos_p1_x, left_pos_p1_y]

        #player 2 possible positions

        up_pos_p2_x = int(curr_pos_p2[0])-1
        up_pos_p2_y = int(curr_pos_p2[1])
        up_pos_p2 = [up_pos_p2_x, up_pos_p2_y]

        down_pos_p2_x = int(curr_pos_p2[0])+1
        down_pos_p2_y = int(curr_pos_p2[1])
        down_pos_p2 = [down_pos_p2_x, down_pos_p2_y]

        right_pos_p2_x = int(curr_pos_p2[0])
        right_pos_p2_y = int(curr_pos_p2[1])+1
        right_pos_p2 = [right_pos_p2_x, right_pos_p2_y]

        left_pos_p2_x = int(curr_pos_p2[0])
        left_pos_p2_y = int(curr_pos_p2[1])-1
        left_pos_p2 = [left_pos_p2_x, left_pos_p2_y]

        #player 3 possible positions

        up_pos_p3_x = int(curr_pos_p3[0])-1
        up_pos_p3_y = int(curr_pos_p3[1])
        up_pos_p3 = [up_pos_p3_x, up_pos_p3_y]

        down_pos_p3_x = int(curr_pos_p3[0])+1
        down_pos_p3_y = int(curr_pos_p3[1])
        down_pos_p3 = [down_pos_p3_x, down_pos_p3_y]

        right_pos_p3_x = int(curr_pos_p3[0])
        right_pos_p3_y = int(curr_pos_p3[1])+1
        right_pos_p3 = [right_pos_p3_x, right_pos_p3_y]

        left_pos_p3_x = int(curr_pos_p3[0])
        left_pos_p3_y = int(curr_pos_p3[1])-1
        left_pos_p3 = [left_pos_p3_x, left_pos_p3_y]

        #player 4 possible positions

        up_pos_p4_x = int(curr_pos_p4[0])-1
        up_pos_p4_y = int(curr_pos_p4[1])
        up_pos_p4 = [up_pos_p4_x, up_pos_p4_y]

        down_pos_p4_x = int(curr_pos_p4[0])+1
        down_pos_p4_y = int(curr_pos_p4[1])
        down_pos_p4 = [down_pos_p4_x, down_pos_p4_y]

        right_pos_p4_x = int(curr_pos_p4[0])
        right_pos_p4_y = int(curr_pos_p4[1])+1
        right_pos_p4 = [right_pos_p4_x, right_pos_p4_y]

        left_pos_p4_x = int(curr_pos_p4[0])
        left_pos_p4_y = int(curr_pos_p4[1])-1
        left_pos_p4 = [left_pos_p4_x, left_pos_p4_y]

        print(curr_pos_p1)
        print("WALLS: ", walls)
        # print(up_pos_p1)

        # player 1 in range check

        up_in_range_p1 = up_pos_p1[0] >= 0 and up_pos_p1[0] <= 9 and up_pos_p1[1] >= 0 and up_pos_p1[1] <= 9
        down_in_range_p1 = down_pos_p1[0] >= 0 and down_pos_p1[0] <= 9 and down_pos_p1[1] >= 0 and down_pos_p1[1] <= 9
        right_in_range_p1 = right_pos_p1[0] >= 0 and right_pos_p1[1] >= 0 and right_pos_p1[0] <= 9 and right_pos_p1[1] <= 9
        left_in_range_p1 = left_pos_p1[0] >= 0 and left_pos_p1[1] >= 0 and left_pos_p1[0] <= 9 and left_pos_p1[1] <= 9

        # player 2 in range check
        
        up_in_range_p2 = up_pos_p2[0] >= 0 and up_pos_p2[1] >= 0 and up_pos_p2[0] <= 9 and up_pos_p2[1] <= 9
        down_in_range_p2 = down_pos_p2[0] >= 0 and down_pos_p2[1] >= 0 and down_pos_p2[0] <= 9 and down_pos_p2[1] <= 9
        right_in_range_p2 = right_pos_p2[0] >= 0 and right_pos_p2[1] >= 0 and right_pos_p2[0] <= 9 and right_pos_p2[1] <= 9
        left_in_range_p2 = left_pos_p2[0] >= 0 and left_pos_p2[1] >= 0 and left_pos_p2[0] <= 9 and left_pos_p2[1] <= 9

        # player 3 in range check
        
        up_in_range_p3 = up_pos_p3[0] >= 0 and up_pos_p3[1] >= 0 and up_pos_p3[0] <= 9 and up_pos_p3[1] <= 9
        down_in_range_p3 = down_pos_p3[0] >= 0 and down_pos_p3[1] >= 0 and down_pos_p3[0] <= 9 and down_pos_p3[1] <= 9
        right_in_range_p3 = right_pos_p3[0] >= 0 and right_pos_p3[1] >= 0 and right_pos_p3[0] <= 9 and right_pos_p3[1] <= 9
        left_in_range_p3 = left_pos_p3[0] >= 0 and left_pos_p3[1] >= 0 and left_pos_p3[0] <= 9 and left_pos_p3[1] <= 9

        # player 4 in range check
        
        up_in_range_p4 = up_pos_p4[0] >= 0 and up_pos_p4[1] >= 0 and up_pos_p4[0] <= 9 and up_pos_p4[1] <= 9
        down_in_range_p4 = down_pos_p4[0] >= 0 and down_pos_p4[1] >= 0 and down_pos_p4[0] <= 9 and down_pos_p4[1] <= 9
        right_in_range_p4 = right_pos_p4[0] >= 0 and right_pos_p4[1] >= 0 and right_pos_p4[0] <= 9 and right_pos_p4[1] <= 9
        left_in_range_p4 = left_pos_p4[0] >= 0 and left_pos_p4[1] >= 0 and left_pos_p4[0] <= 9 and left_pos_p4[1] <= 9

        # check if explored player 1
        up_not_explored_p1 = up_pos_p1 not in currentPosition_p1
        down_not_explored_p1 = down_pos_p1 not in currentPosition_p1
        right_not_explored_p1 = right_pos_p1 not in currentPosition_p1
        left_not_explored_p1 = left_pos_p1 not in currentPosition_p1

        # check if explored player 2
        up_not_explored_p2 = up_pos_p2 not in currentPosition_p2
        down_not_explored_p2 = down_pos_p2 not in currentPosition_p2
        right_not_explored_p2 = right_pos_p2 not in currentPosition_p2
        left_not_explored_p2 = left_pos_p2 not in currentPosition_p2

        # check if explored player 3
        up_not_explored_p3 = up_pos_p3 not in currentPosition_p3
        down_not_explored_p3 = down_pos_p3 not in currentPosition_p3
        right_not_explored_p3 = right_pos_p3 not in currentPosition_p3
        left_not_explored_p3 = left_pos_p3 not in currentPosition_p3

        # check if explored player 4
        up_not_explored_p4 = up_pos_p4 not in currentPosition_p4
        down_not_explored_p4 = down_pos_p4 not in currentPosition_p4
        right_not_explored_p4 = right_pos_p4 not in currentPosition_p4
        left_not_explored_p4 = left_pos_p4 not in currentPosition_p4

        # select player 1 move

        # if (up_pos_p1 not in walls and up_in_range_p1 and up_not_explored_p1):
        #     p1_move = "UP"
        # elif (down_pos_p1 not in walls and down_in_range_p1 and down_not_explored_p1):
        #     p1_move = "DOWN"
        # elif (right_pos_p1 not in walls and right_in_range_p1 and right_in_range_p1):
        #     p1_move = "RIGHT"
        # else:
        #     p1_move = "LEFT"
        
        # # select player 2 move
        
        # if (up_pos_p2 not in walls and up_in_range_p2 and up_not_explored_p2):
        #     p2_move = "UP"
        # elif (down_pos_p2 not in walls and down_in_range_p2 and down_not_explored_p2):
        #     p2_move = "DOWN"
        # elif (right_pos_p2 not in walls and right_in_range_p2 and right_not_explored_p2):
        #     p2_move = "RIGHT"
        # else:
        #     p2_move = "LEFT"
        
        # # select player 3 move
        
        # if (up_pos_p3 not in walls and up_in_range_p3 and up_not_explored_p3):
        #     p3_move = "UP"
        # elif (down_pos_p3 not in walls and down_in_range_p3 and down_not_explored_p3):
        #     p3_move = "DOWN"
        # elif (right_pos_p3 not in walls and right_in_range_p3 and right_not_explored_p3):
        #     p3_move = "RIGHT"
        # else:
        #     p3_move = "LEFT"

        # # select player 4 move
        
        # if (up_pos_p4 not in walls and up_in_range_p4 and up_not_explored_p4):
        #     p4_move = "UP"
        # elif (down_pos_p4 not in walls and down_in_range_p4 and down_not_explored_p4):
        #     p4_move = "DOWN"
        # elif (right_pos_p4 not in walls and right_in_range_p4 and right_not_explored_p4):
        #     p4_move = "RIGHT"
        # else:
        #     p4_move = "LEFT"

        # check for existing players - player 1
        p1_up_p2_check = up_pos_p1 != curr_pos_p2
        p1_up_p3_check = up_pos_p1 != curr_pos_p3
        p1_up_p4_check = up_pos_p1 != curr_pos_p4

        p1_up_check = p1_up_p2_check and p1_up_p3_check and p1_up_p4_check

        p1_down_p2_check = down_pos_p1 != curr_pos_p2
        p1_down_p3_check = down_pos_p1 != curr_pos_p3
        p1_down_p4_check = down_pos_p1 != curr_pos_p4

        p1_down_check = p1_down_p2_check and p1_down_p3_check and p1_down_p4_check

        p1_right_p2_check = right_pos_p1 != curr_pos_p2
        p1_right_p3_check = right_pos_p1 != curr_pos_p3
        p1_right_p4_check = right_pos_p1 != curr_pos_p4

        p1_right_check = p1_right_p2_check and p1_right_p3_check and p1_right_p4_check

        p1_left_p2_check = left_pos_p1 != curr_pos_p2
        p1_left_p3_check = left_pos_p1 != curr_pos_p3
        p1_left_p4_check = left_pos_p1 != curr_pos_p4

        p1_left_check = p1_left_p2_check and p1_left_p3_check and p1_left_p4_check

        # check for existing players - player 2

        p2_up_p1_check = up_pos_p2 != curr_pos_p1
        p2_up_p3_check = up_pos_p2 != curr_pos_p3
        p2_up_p4_check = up_pos_p2 != curr_pos_p4

        p2_up_check = p2_up_p1_check and p2_up_p3_check and p2_up_p4_check

        p2_down_p1_check = down_pos_p2 != curr_pos_p1
        p2_down_p3_check = down_pos_p2 != curr_pos_p3
        p2_down_p4_check = down_pos_p2 != curr_pos_p4

        p2_down_check = p2_down_p1_check and p2_down_p3_check and p2_down_p4_check

        p2_right_p1_check = right_pos_p2 != curr_pos_p1
        p2_right_p3_check = right_pos_p2 != curr_pos_p3
        p2_right_p4_check = right_pos_p2 != curr_pos_p4

        p2_right_check = p2_right_p1_check and p2_right_p3_check and p2_right_p4_check

        p2_left_p1_check = left_pos_p2 != curr_pos_p1
        p2_left_p3_check = left_pos_p2 != curr_pos_p3
        p2_left_p4_check = left_pos_p2 != curr_pos_p4

        p2_left_check = p2_left_p1_check and p2_left_p3_check and p2_left_p4_check

        # check for existing players - player 3

        p3_up_p1_check = up_pos_p3 != curr_pos_p1
        p3_up_p2_check = up_pos_p3 != curr_pos_p2
        p3_up_p4_check = up_pos_p3 != curr_pos_p4

        p3_down_p1_check = down_pos_p3 != curr_pos_p1
        p3_down_p2_check = down_pos_p3 != curr_pos_p2
        p3_down_p4_check = down_pos_p3 != curr_pos_p4

        p3_right_p1_check = right_pos_p3 != curr_pos_p1
        p3_right_p2_check = right_pos_p3 != curr_pos_p2
        p3_right_p4_check = right_pos_p3 != curr_pos_p4

        p3_left_p1_check = left_pos_p3 != curr_pos_p1
        p3_left_p2_check = left_pos_p3 != curr_pos_p2
        p3_left_p4_check = left_pos_p3 != curr_pos_p4

        # check for existing players - player 4

        p4_up_p1_check = up_pos_p4 != curr_pos_p1
        p4_up_p2_check = up_pos_p4 != curr_pos_p2
        p4_up_p3_check = up_pos_p4 != curr_pos_p3

        p4_down_p1_check = down_pos_p4 != curr_pos_p1
        p4_down_p2_check = down_pos_p4 != curr_pos_p2
        p4_down_p3_check = down_pos_p4 != curr_pos_p3

        p4_right_p1_check = right_pos_p4 != curr_pos_p1
        p4_right_p2_check = right_pos_p4 != curr_pos_p2
        p4_right_p3_check = right_pos_p4 != curr_pos_p3

        p4_left_p1_check = left_pos_p4 != curr_pos_p1
        p4_left_p2_check = left_pos_p4 != curr_pos_p2
        p4_left_p3_check = left_pos_p4 != curr_pos_p3

        if (up_pos_p1 not in walls and up_in_range_p1 and p1_up_check):
            p1_move = "UP"
        elif (down_pos_p1 not in walls and down_in_range_p1 and p1_down_check):
            p1_move = "DOWN"
        elif (right_pos_p1 not in walls and right_in_range_p1 and p1_right_check):
            p1_move = "RIGHT"
        else:
            p1_move = "LEFT"
        
        # select player 2 move
        
        if (up_pos_p2 not in walls and up_in_range_p2 and p2_up_check):
            p2_move = "UP"
        elif (down_pos_p2 not in walls and down_in_range_p2 and p2_down_check):
            p2_move = "DOWN"
        elif (right_pos_p2 not in walls and right_in_range_p2 and p2_right_check):
            p2_move = "RIGHT"
        else: #add elif for this too, and if none of them work, then randomize. 
            p2_move = "LEFT"
        
        # select player 3 move
        
        if (up_pos_p3 not in walls and up_in_range_p3):
            p3_move = "UP"
        elif (down_pos_p3 not in walls and down_in_range_p3):
            p3_move = "DOWN"
        elif (right_pos_p3 not in walls and right_in_range_p3):
            p3_move = "RIGHT"
        else:
            p3_move = "LEFT"

        # select player 4 move
        
        if (up_pos_p4 not in walls and up_in_range_p4):
            p4_move = "UP"
        elif (down_pos_p4 not in walls and down_in_range_p4):
            p4_move = "DOWN"
        elif (right_pos_p4 not in walls and right_in_range_p4):
            p4_move = "RIGHT"
        else:
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

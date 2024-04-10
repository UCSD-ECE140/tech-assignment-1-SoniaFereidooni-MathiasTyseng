import os
import json
from dotenv import load_dotenv
import copy
import paho.mqtt.client as paho
from paho import mqtt
import time
import random


# Dictionary to store player positions
player_positions = {}

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
#can also use to update our position dictionary
def on_message(client, userdata, msg):
    """
        Prints a mqtt message to stdout ( used as callback for subscribe )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param msg: the message with topic and payload
    """
    topic = msg.topic
    
    payload = msg.payload.decode()
    

    if topic.endswith("/game_state"):
        player_name = topic.split("/")[-2]
        print(player_name)
        game_state = json.loads(payload)
        print(game_state)
        print("^^game state")
        player_positions[player_name] = game_state["currentPosition"]

        # Determine the next move for the player
        next_move = determine_next_move(player_name, game_state)

        # Publish the move for the player
        client.publish(f"games/{lobby_name}/{player_name}/move", next_move)

    print("message: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))


def euclidean_distance(point1, point2):
    x_diff = point1[0] - point2[0]
    y_diff = point1[1] - point2[1]
    return (x_diff ** 2 + y_diff ** 2) ** 0.5

# Function to determine the next move based on the game state
def determine_next_move(player_name, game_state):
    # simple strategy that moves the player towards the closest coin using our pos dict
    player_pos = game_state["currentPosition"]
    all_coin_positions = game_state["coin1"] + game_state["coin2"] + game_state["coin3"]
    # Get the list of wall positions
    walls = game_state["walls"]

    # Create a list of distances between the player's position and each coin's position
    distances = []
    for coin_pos in all_coin_positions:
        distance = euclidean_distance(coin_pos, player_pos)
        distances.append(distance)


    next_position = copy.copy(player_pos)
    #check that there is a coin within FOV
    if not distances:
        # Try to move in the following order: right, down, left, up
        for direction in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            temp_position = copy.copy(player_pos)
            temp_position[0] += direction[0]
            temp_position[1] += direction[1]
            if temp_position not in walls:
                next_position = temp_position
                break
    else:
        # Find the minimum distance and get the corresponding coin's position
        min_distance = min(distances)
        min_distance_index = distances.index(min_distance)
        closest_coin = all_coin_positions[min_distance_index]

        
        if closest_coin[0] > player_pos[0]:
            next_position[0] += 1
        elif closest_coin[0] < player_pos[0]:
            next_position[0] -= 1
        elif closest_coin[1] > player_pos[1]:
            next_position[1] += 1
        else:
            next_position[1] -= 1
        
        # Check if the next position is a wall
        if next_position in walls:
            # If the next position is a wall, try other directions
            for direction in [[-1, 0], [1, 0], [0, -1], [0, 1]]:
                temp_position = copy.copy(player_pos)
                temp_position[0] += direction[0]
                temp_position[1] += direction[1]
                if temp_position not in walls:
                    next_position = temp_position
                    break


    if next_position[0] > player_pos[0]:
        return "DOWN"
    elif next_position[0] < player_pos[0]:
        return "UP"
    elif next_position[1] > player_pos[1]:
        return "RIGHT"
    else:
        return "LEFT"

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

    client.subscribe(f"games/{lobby_name}/lobby")
    client.subscribe(f'games/{lobby_name}/+/game_state')
    client.subscribe(f'games/{lobby_name}/scores')

    client.publish("new_game", json.dumps({'lobby_name':lobby_name,
                                            'team_name':'ATeam',
                                            'player_name' : player_1}))
    
    client.publish("new_game", json.dumps({'lobby_name':lobby_name,
                                            'team_name':'BTeam',
                                            'player_name' : player_2}))
    
    client.publish("new_game", json.dumps({'lobby_name':lobby_name,
                                        'team_name':'BTeam',
                                        'player_name' : player_3}))

    time.sleep(1) # Wait a second to resolve game start
    #client.subscribe(f"games/{lobby_name}/{player_3}/game_state")
    # client.publish(f"games/{lobby_name}/start", "START")
    # client.publish(f"games/{lobby_name}/{player_1}/move", "UP")
    # client.publish(f"games/{lobby_name}/{player_2}/move", "DOWN")
    # client.publish(f"games/{lobby_name}/{player_3}/move", "DOWN")
    # client.publish(f"games/{lobby_name}/start", "STOP")

    client.publish(f"games/{lobby_name}/start", "START")

    client.loop_start()

    time.sleep(3)

    #onchange
    while(True):
        p1_move = input("Player 1, make your move: ")
        p2_move = input("Player 2, make your move: ")
        p3_move = input("Player 3, make your move: ")

        if(p1_move=='STOP' or p2_move=='STOP' or p3_move=='STOP'):
            client.publish(f"games/{lobby_name}/start", "STOP")
            

        client.publish(f"games/{lobby_name}/{player_1}/move", p1_move)
        client.publish(f"games/{lobby_name}/{player_2}/move", p2_move)
        client.publish(f"games/{lobby_name}/{player_3}/move", p3_move)

        time.sleep(3)

    


    client.loop_forever()
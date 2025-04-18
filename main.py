# Main File to Call All implemented functions.

import gridwars as gw
import usb_port as usb
from card import Card
#ran python3 -m pip install -U pygame==2.6.0 
import pygame
import serial
import threading
import time
import random
from uids import *

#Sources Used: 
# https://www.pygame.org/docs/


has_changed = False
new_card = False
was_placed = False

changed_group = -1
changed_sensor = -1


current_state = 0
uid = 0
ir_matrix = [[False, False, False, False, False, False, False, False],
             [False, False, False, False, False, False, False, False],
             [False, False, False, False, False, False, False, False],
             [False, False, False, False, False, False, False, False],
             [False, False, False, False, False, False, False, False],
             [False, False, False, False, False, False, False, False]]

def verify_state_change(cur, new):
    if cur == 'ERROR' or new == 'ERROR':
        print("State Change involved an ERROR")
        return -1
    elif cur == 'RST' and new != 'IDLE':
        print("State Change from RST to not IDLE")
        return -1
    elif cur == 'IDLE' and new != 'ACTIVEPLACE':
        print("State Change from IDLE to not ACTIVEPLACE")
        return -1
    elif cur == 'ACTIVEPLACE' and new != 'ACTIVEROLE':
        print("State Change from ACTIVEPLACE to not ACTIVEROLE")
        return -1
    elif cur == 'ACTIVEROLE' and new != 'PASSIVEPLACE':
        print("State Change from ACTIVEROLE to not PASSIVEPLACE")
        return -1
    elif cur == 'PASSIVEPLACE' and new != 'IDLE':
        print("State Change from PASSIVEPLACE to not IDLE")
        return -1
    else:
        return 1
    

def convert_ir_matrix_to_coords(group:int, sensor:int): #Untested
    if group == 0 and sensor == 0:
        return (3,1)
    elif group == 0 and sensor == 2:
        return (3,2)
    elif group == 0 and sensor == 4:
        return (4,1)
    elif group == 0 and sensor == 6:
        return (4,2)
    
    if group == 1 and sensor == 0:
        return (3,3)
    elif group == 1 and sensor == 2:
        return (3,4)
    elif group == 1 and sensor == 4:
        return (4,3)
    elif group == 1 and sensor == 6:
        return (4,4)
    
    if group == 2 and sensor == 0:
        return (3,5)
    elif group == 2 and sensor == 2:
        return (3,6)
    elif group == 2 and sensor == 4:
        return (4,5)
    elif group == 2 and sensor == 6:
        return (4,6)

    if group == 3 and sensor == 0:
        return (1,5)
    elif group == 3 and sensor == 2:
        return (1,6)
    elif group == 3 and sensor == 4:
        return (2,5)
    elif group == 3 and sensor == 6:
        return (2,6)

    if group == 4 and sensor == 0:
        return (1,3)
    elif group == 4 and sensor == 2:
        return (1,4)
    elif group == 4 and sensor == 4:
        return (2,3)
    elif group == 4 and sensor == 6:
        return (2,4)

    if group == 5 and sensor == 0:
        return (1,1)
    elif group == 5 and sensor == 2:
        return (1,2)
    elif group == 5 and sensor == 4:
        return (2,1)
    elif group == 5 and sensor == 6:
        return (2,2)


# def read_from_port(ser):
#     global current_state
#     global uid
#     global ir_matrix
#     global has_changed
#     global new_card
#     global was_placed
#     global changed_group
#     global changed_sensor
#     while True:
#         if ser.in_waiting:
#             data = ser.readline()
#             if data:
#                 packet = data.hex()
#                 if data[0] == 0:
#                     header_value = "Game State"
#                 if data[0] == 1:
#                     header_value = "RFID Packet"
#                 elif data[0] == 2:
#                     header_value = "IR Packet"
#                 else:
#                     header_value = "ERROR"
#                     print(data[0])
#                     raise ValueError("Invalid Header Value for newest packet")

#                 if header_value == "Game State": #Game State Packet without RFID
#                     #Next 4 bytes are current_game, I only care about 1st byte
#                     new_state = returnState(packet[2:4])
#                     if verify_state_change(current_state, new_state) == 1:
#                         current_state = new_state
                    
#                 elif header_value == "RFID Packet": 
#                     new_state = returnState(packet[2:4])
#                     if verify_state_change(current_state, new_state) == 1:
#                         current_state = new_state
#                     uid_hex_string = packet[10:18]
#                     uid = int(uid_hex_string, 16)
#                     if int(uid_hex_string, 16) not in uids_list:
#                         print("Failed to find card, no uid stored")
#                         uid = 0
#                     else:
#                         uid = int(uid_hex_string, 16)
#                     print(f"header value = {header_value}")
#                     print(f"current state = {current_state}")
#                     print(f"uid = {uid}")
#                     new_card = True
                    
#                 elif header_value == "IR Packet":
#                     new_state = returnState(packet[2:4])
#                     if verify_state_change(current_state, new_state) == 1:
#                         current_state = new_state
#                     # NEXT 48 BYTES are the IR Matrix data
#                     # Could potentially alter this to send some kind of change data
#                     #   instead of the entire thing
#                     # 48 bytes as a hexstring is 96 characters
#                     num_iter = 0
#                     for i in range(0, 96, 2):
#                         num_iter += 1
#                         sensor = (num_iter % 8) # 0-7
#                         group = (num_iter % 6) # 0-5
#                         new_value = bool(int(packet[i:i+2], 16) == 1)
#                         if ir_matrix[group][sensor] != new_value:
#                             has_changed = True
#                             changed_sensor = sensor
#                             changed_group = group
#                             ir_matrix[group][sensor] = new_value

def read_from_port(ser):
    global current_state
    global uid
    global ir_matrix
    global has_changed
    global new_card
    global was_placed
    global changed_group
    global changed_sensor
    while True:
        if ser.in_waiting:
            # Erroneous Data, skipping to avoid errors
            data = ser.readline()
            if data:
                print(f"data[0] = {data[0]}")
                # print("EOF")
                # break
                if data[0] == 0: #Meaning game state packet
                    data = data[0:5]
                    packet = data.hex()
                    header_value = "Game State Packet"
                    new_state = returnState(packet[2:4])
                    if verify_state_change(current_state, new_state) == 1:
                        current_state = new_state
                if data[0] == 1: #Meaning it is a RFID header
                    data = data[0:9]
                    packet = data.hex()
                    print(len(packet))
                    print((packet))
                    header_value = "RFID Packet"
                    new_state = returnState(packet[2:4])
                    if verify_state_change(current_state, new_state) == 1:
                        current_state = new_state
                    uid_hex_string = packet[10:18]
                    if int(uid_hex_string, 16) not in uids_list:
                        print("Failed to find card, no uid stored")
                        uid = 0
                    else:
                        uid = int(uid_hex_string, 16)
                    print(f"header value = {header_value}")
                    print(f"current state = {current_state}")
                    print(f"uid = {uid}")
                if data[0] == 2: #IR Matrix Data Packet
                    data = data[0:53]
                    packet = data.hex()
                    header_value = "IR Data Packet"
                    num_iter = 0
                    for i in range(0, 96, 2):
                        num_iter += 1
                        sensor = (num_iter % 8) # 0-7
                        group = (num_iter % 6) # 0-5
                        new_value = bool(int(packet[i:i+2], 16) == 1)
                        if ir_matrix[group][sensor] != new_value and new_value == True:
                            has_changed = True # This is a newly placed card
                            changed_sensor = sensor
                            changed_group = group
                            ir_matrix[group][sensor] = new_value
                        elif ir_matrix[group][sensor] != new_value and new_value == False:
                            ir_matrix[group][sensor] = new_value # For removing a Card
                # time.sleep(1)

def returnState(hexstring):
    if hexstring == '00':
        return 'RST'
    elif hexstring == '01':
        return 'IDLE'
    elif hexstring == '02':
        return 'ACTIVEPLACE'
    elif hexstring == '03':
        return 'ACTIVEROLE'
    elif hexstring == '04':
        return 'PASSIVEPLACE'
    else:
        return 'ERROR'


# while True:
#     time.sleep(1)
#     continue


# Defining Player Class
class PlayerClass():
    def __init__(self, playerNum, health, buttonPressed):
        self.playerNum = playerNum # Personal Player Number
        self.health = health # Total Player Health Points
        # self.buttonPressed = buttonPressed # Has Player Pressed Button (0:no or 1:yes)
        self.TheirTurn = -1 # Undecided yet so -1, 1 is Their Turn and 2 is other player's turn
    # Function for Player Damage
    def takeDamage(self, damage):
        self.health -= damage
    


# Defining Card Class
class CardClass():
    def __init__(self, ID):
        self.ID = ID # Individual Card ID from RFID Scan
        self.health = CardStats[ID]["health"] # Card Health Points
        self.power = CardStats[ID]["power"] # Card Power/Attack Points
        self.sleep = CardStats[ID]["sleep"] # Card Sleep Counter (1:sleeping, 0:awake)
        self.mana = CardStats[ID]["mana"] # Card Cost to Play
        self.tapped = CardStats[ID]["tapped"] # Card Tapped State (0:untapped, 1:tapped)


#
#   Bytestream is 53 bytes long
#   
#   first byte: header type (0 for button press, 1 is RFID or 2 is IR)
#   next 4 bytes: when button pressed, sends packet of new state in (4 bytes)
#   if an RFID packet, next 4 bytes are UID in hex. if an IR packet, next 48 bytes are either 1 or 0 each
#


def main():
    global current_state
    global uid
    global has_changed

    current_port = 'COM6' # Change to what your device manager says

    # ser = serial.Serial(port=current_port, baudrate=115200, timeout=1)

    ser = 0 # Swap with this to run without microcontroller


    thread = threading.Thread(target=read_from_port, args=(ser,))
    thread.daemon = True
    # thread.start() # Comment this out to run without Micro

    states = ['RST', 'IDLE', 'ACTIVEPLACE', 'ACTIVEROLE', 'PASSIVEPLACE']

    print(f"Listening on {current_port}...")


    pygame.init()
    screen_info = pygame.display.Info()
    screen = pygame.display.set_mode((screen_info.current_w, screen_info.current_h), pygame.NOFRAME) # NOFRAME for borderless window, FULLSCREEN for fullscreen
    clock = pygame.time.Clock()
    running = True

    placed_cards = []
    
    first_loop = True
    
    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT: #
                running = False

        # fill the screen with a color to wipe away anything from last frame
        screen.fill("blue")

        # RENDER YOUR GAME HERE
        #Create group of cards
        # p1_cards = pygame.sprite.Group() #creates group of cards for P1(bottom of screen)
        
        # this_card = Card(screen, 'joker_card.jpg', 0, (1,1))
        # this_card.place_card()
        
        # this_card2 = Card(screen, 'joker_card.jpg', 0, (1,2))
        # this_card2.place_card()
        
        this_card_1 = Card(screen, path_to_cards[uid_Consort_Radahn_1], uid_Consort_Radahn_1, convert_ir_matrix_to_coords(0,0))
        this_card_1.place_card()
        this_card_2 = Card(screen, path_to_cards[uid_Godfrey_2], uid_Godfrey_2, convert_ir_matrix_to_coords(5,4))
        this_card_2.place_card()
        
        this_card_3 = Card(screen, path_to_cards[uid_Consort_Radahn_1], uid_Consort_Radahn_1, convert_ir_matrix_to_coords(1,0))
        this_card_3.place_card()
        this_card_4 = Card(screen, path_to_cards[uid_Godfrey_2], uid_Godfrey_2, convert_ir_matrix_to_coords(4,4))
        this_card_4.place_card()

        this_card_5 = Card(screen, path_to_cards[uid_Consort_Radahn_1], uid_Consort_Radahn_1, convert_ir_matrix_to_coords(2,0))
        this_card_5.place_card()
        this_card_6 = Card(screen, path_to_cards[uid_Godfrey_2], uid_Godfrey_2, convert_ir_matrix_to_coords(3,4))
        this_card_6.place_card()
        # TEMPORARY COMMENT OUT
        # if(has_changed):
        #     print(CardStats[uid])
        #     for row_i in range(4):
        #         row = []
        #         for col_i in range(6):
        #             # this_card = Card(screen, 'CardArt/joker_card.jpg', 0, (row_i+1,col_i+1))
        #             this_card = Card(screen, path_to_cards[uid], uid, (row_i+1,col_i+1))
        #             this_card.place_card()
        #             row.append(this_card)
        #         placed_cards.append(row)
        if current_state == 0:
            # Maybe have some kind of start Game with button press window
            pass
        elif current_state == "IDLE":
            if first_loop:
                random_num = random.randint(1,2)
                if random_num == 1:
                    print("P1 goes first")
                else:
                    print("P2 goes first")
                first_loop = False
            else: #Swap Whose turn it is
                if random_num == 1:
                    random_num = 2
                else:
                    random_num = 1
                pass
        elif current_state == "ACTIVEPLACE":
            # This PLACES The new card, I need something to keep placing existing cards
            if(has_changed): # IF For when an IR is covered to place that card
                # print(CardStats[uid])
                if uid != 0:
                    # PLACING THE CARD
                    this_card = Card(screen, path_to_cards[uid], uid,
                                    convert_ir_matrix_to_coords(changed_group,changed_sensor))
                    this_card.place_card()
                    placed_cards.append(this_card)
                    uid = 0
                has_changed = False
            if(True): #Calculate to see if card died
                for card in placed_cards:
                    if card.health <= 0:
                        # Install Popup window to tell player to remove that card
                        # Could potentially just do a red X overlapping sprite like Zack said, and wait
                        #   until the player removes it
                        pass
            if(True): #Always Places original cards
                for c in placed_cards:
                    c.place_card() #Keep Placing every Frame
        elif current_state == "ACTIVEROLE":
            # DO IR reading for the rotation of cards
            pass
        elif current_state == "PASSIVEPLACE":
            # TO DO:
            #   make global to tell code to do the game calculations in IDLE next time.
            #       Only startup time of IDLE doesnt need the calculations
            current_state == "BATTLETURN"
            pass
        elif current_state == "BATTLETURN":
            # TO DO:
            #   Game Calculations:
            #       Who won
            #       Etc
            current_state == "DO NOTHING" # Gets code to wait for the micro to change the state
            pass
        elif current_state == "DO NOTHING":
            pass

        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60
        time.sleep(1)

    pygame.quit()

if __name__ == "__main__":
    main()
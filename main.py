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
was_removed = False

changed_group = -1
changed_sensor = -1

num_prev_cycles = 0

current_state = "IDLE" # DEFAULT STARTING VALUE, NOT SENT ON FIRST ITERATION
uid = 0
ir_matrix = [[False, False, False, False, False, False, False, False],
             [False, False, False, False, False, False, False, False],
             [False, False, False, False, False, False, False, False],
             [False, False, False, False, False, False, False, False],
             [False, False, False, False, False, False, False, False],
             [False, False, False, False, False, False, False, False]]
card_location = [[None, None, None, None, None, None, None, None],
             [None, None, None, None, None, None, None, None],
             [None, None, None, None, None, None, None, None],
             [None, None, None, None, None, None, None, None],
             [None, None, None, None, None, None, None, None],
             [None, None, None, None, None, None, None, None]]
group_indexes = []
sensor_indexes = []


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
    print(f"ran convert_ir_matrix_to_coords({group}, {sensor})")
    if group == 0 and sensor == 0:
        return (2,3)
    elif group == 0 and sensor == 2:
        return (2,4)
    elif group == 0 and sensor == 5:
        return (1,4)
    elif group == 0 and sensor == 7:
        return (1,3)
    
    if group == 1 and sensor == 0:
        return (3,4)
    elif group == 1 and sensor == 2:
        return (3,3)
    elif group == 1 and sensor == 5:
        return (4,3)
    elif group == 1 and sensor == 7:
        return (4,4)
    
    if group == 2 and sensor == 0:
        return (3,2)
    elif group == 2 and sensor == 2:
        return (3,1)
    elif group == 2 and sensor == 5:
        return (4,1)
    elif group == 2 and sensor == 7:
        return (4,2)

    if group == 3 and sensor == 0:
        return (3,6)
    elif group == 3 and sensor == 2:
        return (3,5)
    elif group == 3 and sensor == 5:
        return (4,5)
    elif group == 3 and sensor == 7:
        return (4,6)

    if group == 4 and sensor == 0:
        return (2,1)
    elif group == 4 and sensor == 2:
        return (2,2)
    elif group == 4 and sensor == 5:
        return (1,2)
    elif group == 4 and sensor == 7:
        return (1,1)

    if group == 5 and sensor == 0:
        return (2,5)
    elif group == 5 and sensor == 2:
        return (2,6)
    elif group == 5 and sensor == 5:
        return (1,6)
    elif group == 5 and sensor == 7:
        return (1,5)



def read_from_port(ser):
    global current_state
    global uid
    global ir_matrix
    global has_changed
    global new_card
    global was_placed
    global changed_group
    global changed_sensor
    global num_prev_cycles
    global was_removed
    global card_location
    global sensor_indexes
    global group_indexes
    while True:
        if ser.in_waiting:
            # Erroneous Data, skipping to avoid errors
            data = ser.readline()
            if data:
                print(f"data[0] = {data[0]}")
                # print("EOF")
                # break
                if data[0] == 3: #Meaning game state packet
                    data = data[0:5]
                    packet = data.hex()
                    header_value = "Game State Packet"
                    new_state = returnState(packet[2:4])
                    if new_state == "IDLE" and current_state == "PASSIVEPLACE":
                        num_prev_cycles += 1
                    # if verify_state_change(current_state, new_state) == 1:
                    current_state = new_state
                    print(f"current state is now {current_state}")
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
                    print("GOT IR PACKET")
                    header_value = "IR Data Packet"
                    num_iter = 0
                    group_indexes = []
                    sensor_indexes = []
                    for i in range(0, 96, 2):
                        num_iter += 1
                        sensor = (num_iter % 8) # 0-7
                        group = (num_iter % 6) # 0-5
                        new_value = bool(int(packet[i:i+2], 16) == 1)
                        if ir_matrix[group][sensor] != new_value and new_value == True:
                            has_changed = True # This is a newly placed card
                            was_placed = True
                            changed_group = group
                            changed_sensor = sensor
                            ir_matrix[group][sensor] = new_value
                        elif ir_matrix[group][sensor] != new_value and new_value == False:
                            print("THE CARD GOT REMOVED")
                            ir_matrix[group][sensor] = new_value # For removing a Card
                            group_indexes.append(group)
                            sensor_indexes.append(sensor)
                            changed_sensor = sensor
                            changed_group = group
                            has_changed = True
                            was_removed = True
                    print(ir_matrix)
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
    def __init__(self, playerNum, health):
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

isWinner = False # If someone has won the game or not
winningPlayer = -1 # 1 for P1, 2 for P2

def main():
    global current_state
    global uid
    global has_changed
    global num_prev_cycles
    global was_placed
    global was_removed
    global card_location
    global sensor_indexes
    global group_indexes
    
    p1 = PlayerClass(1, 100)
    p2 = PlayerClass(2, 100)

    current_port = 'COM6' # Change to what your device manager says

    ser = serial.Serial(port=current_port, baudrate=115200, timeout=1)

    # ser = 0 # Swap with this to run without microcontroller


    thread = threading.Thread(target=read_from_port, args=(ser,))
    thread.daemon = True
    thread.start() # Comment this out to run without Micro

    states = ['RST', 'IDLE', 'ACTIVEPLACE', 'ACTIVEROLE', 'PASSIVEPLACE']

    print(f"Listening on {current_port}...")


    pygame.init()
    screen_info = pygame.display.Info()
    screen = pygame.display.set_mode((screen_info.current_w, screen_info.current_h), pygame.NOFRAME) # NOFRAME for borderless window, FULLSCREEN for fullscreen
    clock = pygame.time.Clock()
    running = True

    placed_cards = pygame.sprite.Group()
    
    
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

        
        # this_card_1 = Card(screen, path_to_cards[uid_Consort_Radahn_1], uid_Consort_Radahn_1, convert_ir_matrix_to_coords(0,0))
        # this_card_1.place_card()
        # this_card_2 = Card(screen, path_to_cards[uid_Godfrey_2], uid_Godfrey_2, convert_ir_matrix_to_coords(1,0))
        # this_card_2.place_card()
        
        # this_card_3 = Card(screen, path_to_cards[uid_Consort_Radahn_1], uid_Consort_Radahn_1, convert_ir_matrix_to_coords(2,0))
        # this_card_3.place_card()
        # this_card_4 = Card(screen, path_to_cards[uid_Godfrey_2], uid_Godfrey_2, convert_ir_matrix_to_coords(3,0))
        # this_card_4.place_card()

        # this_card_5 = Card(screen, path_to_cards[uid_Consort_Radahn_1], uid_Consort_Radahn_1, convert_ir_matrix_to_coords(4,0))
        # this_card_5.place_card()
        # this_card_6 = Card(screen, path_to_cards[uid_Godfrey_2], uid_Godfrey_2, convert_ir_matrix_to_coords(5,0))
        # this_card_6.place_card()
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
            else:
                #check if game winner
                if num_prev_cycles != 0:
                    current_state = "BATTLETURN"
                    #Swap Whose turn it is
                    if random_num == 1:
                        random_num = 2
                    else:
                        random_num = 1
                    if random_num == 1:
                        print("P1 goes first next")
                    else:
                        print("P2 goes first next")
                    print("BATTLETURN entered")
                    continue

        elif current_state == "ACTIVEPLACE":
            # This PLACES The new card, I need something to keep placing existing cards
            if(has_changed): # IF For when an IR is covered to place that card
                # print(CardStats[uid])
                if(was_placed):
                    if uid != 0:
                        # PLACING THE CARD
                        this_card = Card(screen, path_to_cards[uid], uid,
                                        convert_ir_matrix_to_coords(changed_group,changed_sensor))
                        this_card.place_card()
                        card_location[changed_group][changed_sensor] = this_card
                        placed_cards.add(this_card)
                        print("added card to group")
                        uid = 0
                    was_placed = False
                    has_changed = False
                elif(was_removed):
                    print("was_removed condition")
                    removed_uid = 0
                    len_of_indexes = len(sensor_indexes)
                    for i in (range(len_of_indexes)):
                        if card_location[group_indexes[i]][sensor_indexes[i]] is not None:
                            removed_uid = card_location[group_indexes[i]][sensor_indexes[i]].uid
                            print(f"uid that was removed {removed_uid}")
                            # REMOVE THE CARD
                            this_card = Card(screen, path_to_cards[removed_uid], removed_uid,
                                            convert_ir_matrix_to_coords(group_indexes[i],sensor_indexes[i]))
                            # this_card.place_card()
                            print("WAS REMOVED RAN")
                            placed_cards.remove(card_location[group_indexes[i]][sensor_indexes[i]])
                            print("BELOW SHOULD BE FALSE")
                            print(card_location[group_indexes[i]][sensor_indexes[i]] in placed_cards)
                    group_indexes = []
                    sensor_indexes = []
                    has_changed = False
                    was_removed = False
            if(True): #Always Places original cards
                for c in placed_cards.sprites():
                    if c.health <= 0:
                        # Install Popup window to tell player to remove that card
                        # Could potentially just do a red X overlapping sprite like Zack said, and wait
                        #   until the player removes it
                        pass
                placed_cards.draw(screen)
                 #Keep Placing every Frame
        elif current_state == "ACTIVEROLE":
            # DO IR reading for the rotation of cards
            pass
        elif current_state == "PASSIVEPLACE":
            # TO DO:
            #   make global to tell code to do the game calculations in IDLE next time.
            #       Only startup time of IDLE doesnt need the calculations
            pass
        elif current_state == "BATTLETURN":
            # TO DO:
            #   Game Calculations:
            #       Who won
            #       Etc
            
            # DO DAMAGE CALCULATION HERE
            #p1.takeDamage(100) is death
            
            if p1.health <= 0:
                isWinner = True
                winningPlayer = 1
                current_state = "WINSCREEN"
            elif p2.health <= 0:
                isWinner = True
                winningPlayer = 2
                current_state = "WINSCREEN"
            
            # If nobody won or lost go back to IDLE
            current_state = "IDLE" # Gets code to wait for the micro to change the state
        elif current_state == "WINSCREEN":
            # TO DO:
            #   Display some kind of win screen window
            pass

        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60
        time.sleep(1)

    pygame.quit()

if __name__ == "__main__":
    main()
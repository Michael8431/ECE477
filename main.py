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
# from pop_up_screens import *
from tkinter import*
from PIL import ImageTk, Image
from pop_up_screens import *
from dead_card_sprite import *


#Sources Used: 
# https://www.pygame.org/docs/


has_changed = False
new_card = False
was_placed = False
was_removed = False

changed_group = -1
changed_sensor = -1

do_calculations = 0

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
group_place_indexes = []
sensor_place_indexes = []


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
        return (3,1)
    elif group == 0 and sensor == 2:
        return (3,2)
    elif group == 0 and sensor == 5:
        return (4,2)
    elif group == 0 and sensor == 7:
        return (4,1)
    
    if group == 1 and sensor == 0:
        return (3,3)
    elif group == 1 and sensor == 2:
        return (3,4)
    elif group == 1 and sensor == 5:
        return (4,4)
    elif group == 1 and sensor == 7:
        return (4,3)
    
    if group == 2 and sensor == 0:
        return (3,5)
    elif group == 2 and sensor == 2:
        return (3,6)
    elif group == 2 and sensor == 5:
        return (4,6)
    elif group == 2 and sensor == 7:
        return (4,5)

    if group == 3 and sensor == 0:
        return (2,2)
    elif group == 3 and sensor == 2:
        return (2,1)
    elif group == 3 and sensor == 5:
        return (1,1)
    elif group == 3 and sensor == 7:
        return (1,2)

    if group == 4 and sensor == 0:
        return (2,4)
    elif group == 4 and sensor == 2:
        return (2,3)
    elif group == 4 and sensor == 5:
        return (1,3)
    elif group == 4 and sensor == 7:
        return (1,4)

    if group == 5 and sensor == 0:
        return (2,6)
    elif group == 5 and sensor == 2:
        return (2,5)
    elif group == 5 and sensor == 5:
        return (1,5)
    elif group == 5 and sensor == 7:
        return (1,6)

# def convert_ir_matrix_to_coords_role():



def read_from_port(ser):
    global current_state
    global uid
    global ir_matrix
    global has_changed
    global new_card
    global was_placed
    global changed_group
    global changed_sensor
    global do_calculations
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
                        print("ONE FULL CYCLE")
                        do_calculations = 1
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
                    print(f"new state is {new_state}")
                    # if verify_state_change(current_state, new_state) == 1:
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
                    # data = data[0:53]
                    packet = data.hex()
                    print("GOT IR PACKET")
                    header_value = "IR Data Packet"
                    num_iter = 0
                    num_group = 0
                    num_sensor = 0
                    group_indexes = []
                    sensor_indexes = []
                    group_place_indexes = []
                    sensor_place_indexes = []
                    for i in range(10, 101, 2):
                        num_group = int(num_iter / 8)
                        if(num_sensor >= 8):
                            num_sensor = 0
                        # so group 0 is index 10 through 17
                        # so group 1 is index 18 through 25
                        # sensor = (num_iter % 8) # 0-7
                        # group = (num_iter % 6) # 0-5
                        new_value = bool(int(packet[i:i+2], 16) == 1)
                        # print(new_value)
                        if ir_matrix[num_group][num_sensor] != new_value and new_value == True:
                            print("NEW VALUE WAS TRUE")
                            has_changed = True # This is a newly placed card
                            was_placed = True
                            # was_removed = False
                            changed_group = num_group
                            changed_sensor = num_sensor
                            group_place_indexes.append(changed_group)
                            sensor_place_indexes.append(changed_sensor)
                            ir_matrix[num_group][num_sensor] = new_value
                            break
                        elif ir_matrix[num_group][num_sensor] != new_value and new_value == False:
                            print("THE CARD GOT REMOVED")
                            ir_matrix[num_group][num_sensor] = new_value # For removing a Card
                            group_indexes.append(num_group)
                            sensor_indexes.append(num_sensor)
                            changed_sensor = num_sensor
                            changed_group = num_group
                            has_changed = True
                            was_removed = True
                        num_sensor += 1
                        num_iter += 1
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
        self.theirTurn = -1 # Undecided yet so -1, 1 is Their Turn and 2 is other player's turn
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



def card_died_animation(screen, placed_cards: pygame.sprite.Group, dead_card: Card):
    # Place RED X on top of card
    # Wait 5 Seconds
    # Remove Red X
    # Remove Card
    red_x = Dead_Card_Sprite(dead_card)
    placed_cards.add(red_x)
    start_time = time.time()
    cur_time = time.time()
    while cur_time - start_time < 3: # Keep red X on for 2 Seconds
        placed_cards.draw(screen)
        cur_time = time.time()
    placed_cards.remove(red_x) # Remove Red X after 2 Seconds

    return


#
#   Bytestream is 53 bytes long
#   
#   first byte: header type (0 for button press, 1 is RFID or 2 is IR)
#   next 4 bytes: when button pressed, sends packet of new state in (4 bytes)
#   if an RFID packet, next 4 bytes are UID in hex. if an IR packet, next 48 bytes are either 1 or 0 each
#

p1 = PlayerClass(playerNum=1, health=20)
p2 = PlayerClass(playerNum=2, health=20)

winningPlayer = -1 # 1 for P1, 2 for P2

p1_damage_taken = 0
p2_damage_taken = 0
group_damage = [0,0,0,0,0,0]
group_health = [0,0,0,0,0,0]


# global player1
# global player2

stop_event_start_game = threading.Event()
stop_event_end_game = threading.Event()



start_screen_on = True


def main():
    global current_state
    global uid
    global has_changed
    global do_calculations
    global was_placed
    global was_removed
    global card_location
    global sensor_indexes
    global group_indexes
    global winningPlayer
    global turn_swap_needed
    global p1
    global p2
    global p1_damage_taken
    global p2_damage_taken
    global group_damage
    global group_health
    global stop_event_start_game
    global stop_event_start_game
    global start_screen_on
    global root
    global changed_group
    global changed_sensor
    


    current_port = '/dev/ttyUSB0' # Change to what your device manager says

    ser = serial.Serial(port=current_port, baudrate=115200, timeout=1)

    # ser = 0 # Swap with this to run without microcontroller

    startScreen()

    thread = threading.Thread(target=read_from_port, args=(ser,))
    thread.daemon = True
    thread.start() # Comment this out to run without Micro

    states = ['RST', 'IDLE', 'ACTIVEPLACE', 'ACTIVEROLE', 'PASSIVEPLACE']

    print(f"Listening on {current_port}...")



    pygame.init()
    
    screen_info = pygame.display.Info()
    point_size = 500
    font = pygame.font.Font(None, point_size)
    font_state = pygame.font.Font(None, point_size//5)
    screen = pygame.display.set_mode((screen_info.current_w, screen_info.current_h), pygame.NOFRAME) # NOFRAME for borderless window, FULLSCREEN for fullscreen
    clock = pygame.time.Clock()
    running = True

    placed_cards = pygame.sprite.Group()
    
    
    first_loop = True
    
    turn_swap_needed = False
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: #
                running = False

        screen.fill("black")
        text_p1 = f"P1:{p1.health}HP"
        txt_surface = font.render(text_p1, True, pygame.Color('green'))
        txt_rect = txt_surface.get_rect()
        w, h = screen.get_size()
        txt_rect.bottom = h
        txt_rect.centerx = w//2

        screen.blit(txt_surface, txt_rect)

        text_p2 = f"P2:{p2.health}HP"
        txt_surface_2 = font.render(text_p2, True, pygame.Color('green'))
        txt_rect_2 = txt_surface_2.get_rect()
        txt_rect_2.top = 0
        txt_rect_2.centerx = w//2
        screen.blit(txt_surface_2, txt_rect_2)

        ###########################
        text_end_turn = "<-- End Phase"
        words = text_end_turn.split(' ')

        x = 0
        # y = h // 2
        y = h // 3

        line_spacing = 5
        max_width = 200

        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            test_surface = font_state.render(test_line, True, pygame.Color('green'))
            if test_surface.get_width() > max_width:
                lines.append(current_line)
                current_line = word
            else:
                current_line = test_line

        if current_line:
            lines.append(current_line)

        for line in lines:
            txt_surface_end_turn = font_state.render(line, True, pygame.Color('green'))
            txt_rect_end = txt_surface_end_turn.get_rect()
            txt_rect_end.left = 0
            txt_rect_end.top = y
            screen.blit(txt_surface_end_turn, txt_rect_end)
            y += txt_surface_end_turn.get_height() + line_spacing

        ###########################

        if p1.theirTurn != -1 and p2.theirTurn != -1:
            this_player_turn = "P1's Turn" if p1.theirTurn == 1 else "P2's Turn"
            # print(f"P1={p1.theirTurn} P2={p2.theirTurn}")
            player_message = ""
            if current_state == "IDLE":
                player_message = "Begin Turn with Button"
            elif current_state == "ACTIVEPLACE":
                player_message = "Scan and Place"
            elif current_state == "ACTIVEROLE":
                player_message = "Rotate Cards"
            elif current_state == "PASSIVEPLACE":
                player_message = "Scan and Place"
            text_state = f"{this_player_turn}: {player_message}"
            txt_surface_state = font_state.render(text_state, True, pygame.Color('green'))
            txt_rect_state = txt_surface_state.get_rect()
            txt_rect_state.center = (w//2, h//2)
            
            screen.blit(txt_surface_state, txt_rect_state)


        if current_state == 0:
            pass
        elif current_state == "IDLE":
            placed_cards.draw(screen)
            if first_loop:
                random_num = random.randint(1,2)
                if random_num == 1:
                    p1.theirTurn = 1
                    p2.theirTurn = 2
                    print("P1 goes first")
                else:
                    p2.theirTurn = 1
                    p1.theirTurn = 2
                    print("P2 goes first")
                first_loop = False
            else:
                #check if game winner
                if do_calculations == 1:
                    do_calculations = 0
                    current_state = "BATTLETURN"
                    continue
                elif turn_swap_needed:
                    #Swap Whose turn it is
                    if random_num == 1:
                        random_num = 2
                    else:
                        random_num = 1
                    if random_num == 1:
                        p1.theirTurn = 1
                        p2.theirTurn = 2
                        print("P1 goes first next")
                    else:
                        p2.theirTurn = 1
                        p1.theirTurn = 2
                        print("P2 goes first next")
                    turn_swap_needed = False

        elif current_state == "ACTIVEPLACE":
            # This PLACES The new card, I need something to keep placing existing cards
            if(has_changed): # IF For when an IR is covered to place that card
                # print(CardStats[uid])
                if(was_placed):
                    if uid != 0:
                                    
                        # PLACING THE CARD
                        this_card = Card(screen, path_to_cards[uid], uid,
                                        convert_ir_matrix_to_coords(changed_group,changed_sensor))
                        # this_card.place_card()
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
                            card_location[group_indexes[i]][sensor_indexes[i]] = None #REMOVING IT
                    group_indexes = []
                    sensor_indexes = []
                    has_changed = False
                    was_removed = False
            if(True): #Always Places original cards
                placed_cards.draw(screen)
                 #Keep Placing every Frame
        elif current_state == "ACTIVEROLE":
            # print(has_changed)
            # print(was_placed)
            if(has_changed):
                if(was_placed):
                    # if changed_group <= 2:
                    if changed_sensor == 1 or changed_sensor == 3:
                        if card_location[changed_group][changed_sensor-1] is not None and card_location[changed_group][changed_sensor] is None:
                            card_location[changed_group][changed_sensor] = card_location[changed_group][changed_sensor-1]
                            print("ROLE WAS PLACED")
                    elif changed_sensor == 4 or changed_sensor == 6:
                        if card_location[changed_group][changed_sensor+1] is not None and card_location[changed_group][changed_sensor] is None:
                            card_location[changed_group][changed_sensor] = card_location[changed_group][changed_sensor+1]
                            print("ROLE WAS PLACED")


                    print("has_changed and was_placed")
                    if changed_sensor == 1 or changed_sensor == 3:
                        card_location[changed_group][changed_sensor] = card_location[changed_group][changed_sensor-1]
                    elif changed_sensor == 4 or changed_sensor == 6:
                        card_location[changed_group][changed_sensor] = card_location[changed_group][changed_sensor+1]
                    placed_cards.remove(card_location[changed_group][changed_sensor])
                    card_location[changed_group][changed_sensor].rotate_card()
                    placed_cards.add(card_location[changed_group][changed_sensor])
                    print("ROTATED SPRITE ADDED")
                            
                    
                    was_placed = False
                    has_changed = False
                elif(was_removed):
                    if changed_sensor == 1 or changed_sensor == 3:
                        if card_location[changed_group][changed_sensor-1] is not None:
                            card_location[changed_group][changed_sensor] = None
                    elif changed_sensor == 4 or changed_sensor == 6:
                        if card_location[changed_group][changed_sensor+1] is not None:
                            card_location[changed_group][changed_sensor] = None

                    for i in range(len(card_location)):
                        for j in range(len(card_location[i])):
                            if j+1 < 8:
                                if card_location[i][j+1] is None: # No longer rotated
                                        if card_location[i][j] is not None: # Card is still placed
                                            placed_cards.remove(card_location[i][j]) #remove unrotated version
                                            card_location[i][j].unrotate_card()
                                            placed_cards.add(card_location[i][j])  
                                            print("UNROTATED SPRITE ADDED")
                    has_changed = False
                    was_removed = False
            placed_cards.draw(screen)
        elif current_state == "PASSIVEPLACE":
            # This PLACES The new card, I need something to keep placing existing cards
            if(has_changed): # IF For when an IR is covered to place that card
                # print(CardStats[uid])
                if(was_placed):
                    if uid != 0:
                        # PLACING THE CARD
                        this_card = Card(screen, path_to_cards[uid], uid,
                                        convert_ir_matrix_to_coords(changed_group,changed_sensor))
                        # this_card.place_card()
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
                            card_location[group_indexes[i]][sensor_indexes[i]] = None #REMOVING IT
                    group_indexes = []
                    sensor_indexes = []
                    has_changed = False
                    was_removed = False
            if(True): #Always Places original cards
                placed_cards.draw(screen)
                 #Keep Placing every Frame
            
        elif current_state == "BATTLETURN":
            # TO DO:
            #   Game Calculations:
            #       Who won
            #       Etc
            
            # DO DAMAGE CALCULATION HERE
            #p1.takeDamage(100) is death
            # NOW THE FUN PART
            # group 0 attacks group 3
            # group 1 attacks group 4
            # group 2 attacks group 5
            # sensor 0,2,5,7
            p1_blockers = []
            p1_attackers = []
            p2_blockers = []
            p2_attackers = []

            
            for group_idx in range(6):
                for sensor_idx in range(8):
                    if sensor_idx == 0 or sensor_idx == 2 or sensor_idx == 5 or sensor_idx == 7:
                        if card_location[group_idx][sensor_idx] is not None:
                            print(f"FOUND CARD CALLED {card_location[group_idx][sensor_idx].name}")
                            print(f"Card is Rotated = {card_location[group_idx][sensor_idx].is_rotated}")
                            print(f"Card damage = {card_location[group_idx][sensor_idx].power}")
                            if card_location[group_idx][sensor_idx].is_rotated:
                                if group_idx <= 2:
                                    p1_attackers.append(card_location[group_idx][sensor_idx])
                                else:
                                    p2_attackers.append(card_location[group_idx][sensor_idx])
                                group_damage[group_idx] += card_location[group_idx][sensor_idx].power
                                print("GROUP DAMAGE")
                                print(group_damage)
                            else:
                                if group_idx <= 2:
                                    p1_blockers.append(card_location[group_idx][sensor_idx])
                                else:
                                    p2_blockers.append(card_location[group_idx][sensor_idx])
                                # print("GROUP HEALTH")
                                # print(group_health)
            for group_idx in range(len(group_damage)):
                if group_idx <= 2:
                    # p2_damage_taken = group_damage[group_idx] - group_health[3 + group_idx]
                    p2_damage_taken = group_damage[group_idx]
                    for card in p2_blockers:
                        if p2_damage_taken > card.health:
                            p2_damage_taken -= card.health
                            card.health = 0
                            
                            print(f"{card.name} GOT COOKED, remove it from the board")
                            placed_cards.remove(card)
                    print(f"p2 took {p2_damage_taken} damage")
                    if p2_damage_taken > 0:
                        p2.health -= p2_damage_taken
                else:
                    p1_damage_taken = group_damage[group_idx]
                    for card in p1_blockers:
                        if p1_damage_taken > card.health:
                            p1_damage_taken -= card.health
                            card.health = 0
                            print(f"{card.name} GOT COOKED, remove it from the board")
                            card_died_animation(screen,placed_cards,card)
                            placed_cards.remove(card)
                    print(f"p1 took {p1_damage_taken} damage")
                    if p1_damage_taken > 0:
                        p1.health -= p1_damage_taken
                if p1.health <= 0:
                    winningPlayer = 2
                    current_state = "WINSCREEN"
                    break
                if p2.health <= 0:
                    winningPlayer = 1
                    current_state = "WINSCREEN"
                    break
            p1_damage_taken = 0
            p2_damage_taken = 0
            group_damage = [0,0,0,0,0,0]
            group_health = [0,0,0,0,0,0]
            if current_state != "WINSCREEN":
                print(f"p1 has {p1.health} health remaining")
                print(f"p2 has {p2.health} health remaining")
                turn_swap_needed = True # Only reached if we never redirected to WINSCREEN
                current_state = "IDLE" # Go back to start of loop


        elif current_state == "WINSCREEN":
            # TO DO:
            #   Display some kind of win screen window
            if winningPlayer == 1:
                print("PLAYER 1 WON")
                endScreen(1,0)
                break
            elif winningPlayer == 2:
                print("PLAYER 2 WON")
                endScreen(0,1)
                break
            else:
                print("NOBODY WON YET, SWAPPING FIRST TURN in IDLE NEXT TIME")
            current_state = "IDLE"

        # Add Player Health Text to background
        # print("THIS RAN BLIT")


        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60
        time.sleep(1)

    pygame.quit()

if __name__ == "__main__":
    main()
# Main File to Call All implemented functions.

import gridwars as gw
import usb_port as usb
from card import Card
#ran python3 -m pip install -U pygame==2.6.0 
import pygame
import serial
import threading
import time

#Sources Used: 
# https://www.pygame.org/docs/




has_changed = False

current_state = 0
uid = 0
ir_matrix = [[False, False, False, False, False, False, False, False],
             [False, False, False, False, False, False, False, False],
             [False, False, False, False, False, False, False, False],
             [False, False, False, False, False, False, False, False],
             [False, False, False, False, False, False, False, False],
             [False, False, False, False, False, False, False, False]]

def read_from_port(ser):
    global current_state
    global uid
    global has_changed
    print("THIS RAN")
    while True:
        if ser.in_waiting:
            data = ser.readline()
            if data:
                if data[0] == 1: #Meaning it is a RFID header
                    packet = data.hex()
                    header_value = "RFID Packet" if int(packet[0:2], 16) == 1 else "IR Packet"
                    current_state = returnState(packet[2:4])
                    uid_hex_string = packet[10:18]
                    uid = int(uid_hex_string, 16)
                    print(f"header value = {header_value}")
                    print(f"current state = {current_state}")
                    print(f"uid = {uid}")
                    has_changed = True


# CODE TO RECEIEVE SOMETHING FROM THE RASPBERRY PI







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
        self.buttonPressed = buttonPressed # Has Player Pressed Button (0:no or 1:yes)

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

uid_Mechazawa_1 = 0
uid_Mechazawa_2 = 1
uid_Crungus_1 = 2
uid_Crungus_2 = 3
uid_Exodia_1 = 4
uid_Exodia_2 = 5
uid_Shabeel_1 = 6
uid_Shabeel_2 = 7
uid_Powerplex_1 = 8
uid_Powerplex_2 = 9
uid_The_Pig_1 = 10
uid_The_Pig_2 = 11
uid_Gurren_Lagann_1 = 12
uid_Gurren_Lagann_2 = 13
uid_The_Impractical_Jokers_1 = 14
uid_The_Impractical_Jokers_2 = 15
uid_Magikarp_1 = 16
uid_Magikarp_2 = 17
uid_Moto_Mechazawa_1 = 18
uid_Moto_Mechazawa_2 = 19
uid_Mini_Mechazawa_1 = 20
uid_Mini_Mechazawa_2 = 21
uid_Batman_1 = 22
uid_Batman_2 = 23
uid_Bubble_Buddy_1 = 24
uid_Bubble_Buddy_2 = 25
uid_Dirty_Bubble_1 = 26
uid_Dirty_Bubble_2 = 27
uid_Beast_Titan_1 = 28
uid_Beast_Titan_2 = 29
uid_Consort_Radahn_1 = 30
uid_Consort_Radahn_2 = 31
uid_Godfrey_1 = 32
uid_Godfrey_2 = 33
uid_Schnitzel_1 = 34
uid_Schnitzel_2 = 35


# Lookup Table for Card Stats
CardStats = {
    uid_Mechazawa_1:              {"name": "Mechazawa", "health": 5, "power": 1, "sleep": 1, "mana": 2, "tapped": 0}, 
    uid_Mechazawa_2:              {"name": "Mechazawa", "health": 5, "power": 1, "sleep": 1, "mana": 2, "tapped": 0}, 
    uid_Crungus_1:                {"name": "Crungus", "health": 2, "power": 1, "sleep": 1, "mana": 1, "tapped": 0}, 
    uid_Crungus_2:                {"name": "Crungus", "health": 2, "power": 1, "sleep": 1, "mana": 1, "tapped": 0}, 
    uid_Exodia_1:                 {"name": "Exodia", "health": 10, "power": 10, "sleep": 1, "mana": 5, "tapped": 0}, 
    uid_Exodia_2:                 {"name": "Exodia", "health": 10, "power": 10, "sleep": 1, "mana": 5, "tapped": 0}, 
    uid_Shabeel_1:                {"name": "Shabeel", "health": 4, "power": 4, "sleep": 1, "mana": 3, "tapped": 0}, 
    uid_Shabeel_2:                {"name": "Shabeel", "health": 4, "power": 4, "sleep": 1, "mana": 3, "tapped": 0}, 
    uid_Powerplex_1:              {"name": "Powerplex", "health": 3, "power": 2, "sleep": 1, "mana": 2, "tapped": 0},
    uid_Powerplex_2:              {"name": "Powerplex", "health": 3, "power": 2, "sleep": 1, "mana": 2, "tapped": 0},
    uid_The_Pig_1:                {"name": "The Pig", "health": 99, "power": 99, "sleep": 0, "mana": 0, "tapped": 0}, 
    uid_The_Pig_2:                {"name": "The Pig", "health": 99, "power": 99, "sleep": 0, "mana": 0, "tapped": 0}, 
    uid_Gurren_Lagann_1:          {"name": "Gurren Lagann", "health": 5, "power": 3, "sleep": 1, "mana": 3, "tapped": 0}, 
    uid_Gurren_Lagann_2:          {"name": "Gurren Lagann", "health": 5, "power": 3, "sleep": 1, "mana": 3, "tapped": 0}, 
    uid_The_Impractical_Jokers_1: {"name": "The Impractical Jokers", "health": 1, "power": 2, "sleep": 1, "mana": 1, "tapped": 0}, 
    uid_The_Impractical_Jokers_2: {"name": "The Impractical Jokers", "health": 1, "power": 2, "sleep": 1, "mana": 1, "tapped": 0}, 
    uid_Magikarp_1:               {"name": "Magikarp", "health": 2, "power": 1, "sleep": 1, "mana": 1, "tapped": 0}, 
    uid_Magikarp_2:               {"name": "Magikarp", "health": 2, "power": 1, "sleep": 1, "mana": 1, "tapped": 0}, 
    uid_Moto_Mechazawa_1:         {"name": "Moto-Mechazawa", "health": 2, "power": 5, "sleep": 1, "mana": 3, "tapped": 0},
    uid_Moto_Mechazawa_2:         {"name": "Moto-Mechazawa", "health": 2, "power": 5, "sleep": 1, "mana": 3, "tapped": 0},
    uid_Mini_Mechazawa_1:         {"name": "Mini-Mechazawa", "health": 2, "power": 3, "sleep": 1, "mana": 2, "tapped": 0}, 
    uid_Mini_Mechazawa_2:         {"name": "Mini-Mechazawa", "health": 2, "power": 3, "sleep": 1, "mana": 2, "tapped": 0}, 
    uid_Batman_1:                 {"name": "Batman", "health": 4, "power": 6, "sleep": 1, "mana": 4, "tapped": 0}, 
    uid_Batman_2:                 {"name": "Batman", "health": 4, "power": 6, "sleep": 1, "mana": 4, "tapped": 0}, 
    uid_Bubble_Buddy_1:           {"name": "Bubble Buddy", "health": 1, "power": 4, "sleep": 1, "mana": 2, "tapped": 0}, 
    uid_Bubble_Buddy_2:           {"name": "Bubble Buddy", "health": 1, "power": 4, "sleep": 1, "mana": 2, "tapped": 0}, 
    uid_Dirty_Bubble_1:           {"name": "Dirty Bubble", "health": 4, "power": 1, "sleep": 1, "mana": 3, "tapped": 0}, 
    uid_Dirty_Bubble_2:           {"name": "Dirty Bubble", "health": 4, "power": 1, "sleep": 1, "mana": 3, "tapped": 0}, 
    uid_Beast_Titan_1:            {"name": "Beast Titan", "health": 12, "power": 8, "sleep": 1, "mana": 6, "tapped": 0},
    uid_Beast_Titan_2:            {"name": "Beast Titan", "health": 12, "power": 8, "sleep": 1, "mana": 6, "tapped": 0},
    uid_Consort_Radahn_1:         {"name": "Consort Radahn", "health": 8, "power": 13, "sleep": 1, "mana": 5, "tapped": 0}, 
    uid_Consort_Radahn_2:         {"name": "Consort Radahn", "health": 8, "power": 13, "sleep": 1, "mana": 5, "tapped": 0}, 
    uid_Godfrey_1:                {"name": "Godfrey", "health": 10, "power": 5, "sleep": 1, "mana": 4, "tapped": 0}, 
    uid_Godfrey_2:                {"name": "Godfrey", "health": 10, "power": 5, "sleep": 1, "mana": 4, "tapped": 0}, 
    uid_Schnitzel_1:              {"name": "Schnitzel", "health": 7, "power": 2, "sleep": 1, "mana": 3, "tapped": 0},
    uid_Schnitzel_2:              {"name": "Schnitzel", "health": 7, "power": 2, "sleep": 1, "mana": 3, "tapped": 0}
    # Keep adding more if needed
}


#
#   Bytestream is 53 bytes long
#   
#   first byte: header type (0 for button press, 1 is RFID or 2 is IR)
#   next 4 bytes: when button pressed, sends packet of new state in (4 bytes)
#   if an RFID packet, next 4 bytes are UID in hex. if an IR packet, next 48 bytes are either 1 or 0 each
#


# State Machine
# game_state = ["IDLE", "RST", "PLACEMENT", "ATTACK", "DEFENSE", "GAMEOVER"]
# current_state = -1
# activePlayer = 1
# nextPlayer = 0
# buttonPressed = 0

# match game_state:
#     case "IDLE":
#         print("Idle State!")
#     case "RST":
#         print("Reset!")
#     case "PLACEMENT":
#         print("Placement!")
#         if (buttonPressed):
#             current_state = "ATTACK"
#     case "ATTACK":
#         print("Attack!")
#         if (buttonPressed):
#             current_state = "DEFENSE"
#     case "DEFENSE":
#         print("Defense!")
#         if (buttonPressed):
#             # Defense is last phase during turn, so swap active player when button pressed
#             temp = activePlayer
#             activePlayer = nextPlayer
#             nextPlayer = temp
#             current_state = "PLACEMENT"
#     case "GAMEOVER":
#         print("Gameover!")
# def StateMachine():
#     packetReceived = 0
#     data = []
    
#     while (True):
#         # If no packet received, restart
#         if not packetReceived:
#             continue 
        
#         packetReceived = 0
#         data = data.append(bytestream)
#         header = data[0]
#         # Check packet after continue

#         # If not an RFID type, restart
#         if (header != 1):
#             continue

#         ID = data[1:5]
#         while(True):


path_to_cards = {
    uid_Mechazawa_1: "CardArt/Mechazawa.jpg",
    uid_Mechazawa_2: "CardArt/Mechazawa.jpg",
    uid_Crungus_1: "CardArt/Crungus.jpg",
    uid_Crungus_2: "CardArt/Crungus.jpg",
    uid_Exodia_1: "CardArt/Exodia.jpg",
    uid_Exodia_2: "CardArt/Exodia.jpg",
    uid_Shabeel_1: "CardArt/Shabeel.jpg",
    uid_Shabeel_2: "CardArt/Shabeel.jpg",
    uid_Powerplex_1: "CardArt/Powerplex.jpg",
    uid_Powerplex_2: "CardArt/Powerplex.jpg",
    uid_The_Pig_1: "CardArt/The_Pig.jpg",
    uid_The_Pig_2: "CardArt/The_Pig.jpg",
    uid_Gurren_Lagann_1: "CardArt/Gurren_Lagann.jpg",
    uid_Gurren_Lagann_2: "CardArt/Gurren_Lagann.jpg",
    uid_The_Impractical_Jokers_1: "CardArt/The_Impractical_Jokers.jpg",
    uid_The_Impractical_Jokers_2: "CardArt/The_Impractical_Jokers.jpg",
    uid_Magikarp_1: "CardArt/Magikarp.jpg",
    uid_Magikarp_2: "CardArt/Magikarp.jpg",
    uid_Moto_Mechazawa_1: "CardArt/Moto_Mechazawa.jpg",
    uid_Moto_Mechazawa_2: "CardArt/Moto_Mechazawa.jpg",
    uid_Mini_Mechazawa_1: "CardArt/Mini_Mechazawa.jpg",
    uid_Mini_Mechazawa_2: "CardArt/Mini_Mechazawa.jpg",
    uid_Batman_1: "CardArt/Batman.jpg",
    uid_Batman_2: "CardArt/Batman.jpg",
    uid_Bubble_Buddy_1: "CardArt/Bubble_Buddy.jpg",
    uid_Bubble_Buddy_2: "CardArt/Bubble_Buddy.jpg",
    uid_Dirty_Bubble_1: "CardArt/Dirty_Bubble.jpg",
    uid_Dirty_Bubble_2: "CardArt/Dirty_Bubble.jpg",
    uid_Beast_Titan_1: "CardArt/Beast_Titan.jpg",
    uid_Beast_Titan_2: "CardArt/Beast_Titan.jpg",
    uid_Consort_Radahn_1: "CardArt/Consort_Radahn.jpg",
    uid_Consort_Radahn_2: "CardArt/Consort_Radahn.jpg",
    uid_Godfrey_1: "CardArt/Godfrey.jpg",
    uid_Godfrey_2: "CardArt/Godfrey.jpg",
    uid_Schnitzel_1: "CardArt/Schnitzel.jpg",
    uid_Schnitzel_2: "CardArt/Schnitzel.jpg"
}





def main():
    global current_state
    global uid
    global has_changed

    ser = serial.Serial(port='COM3', baudrate=115200, timeout=1)


    thread = threading.Thread(target=read_from_port, args=(ser,))
    thread.daemon = True
    thread.start()

    states = ['RST', 'IDLE', 'ACTIVEPLACE', 'ACTIVEROLE', 'PASSIVEPLACE']

    print("Listening on COM6...")


    pygame.init()
    screen_info = pygame.display.Info()
    screen = pygame.display.set_mode((screen_info.current_w, screen_info.current_h), pygame.NOFRAME) # NOFRAME for borderless window, FULLSCREEN for fullscreen
    clock = pygame.time.Clock()
    running = True

    
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
        if(has_changed):
            jokers = []
            for row_i in range(4):
                row = []
                for col_i in range(6):
                    this_card = Card(screen, 'CardArt/joker_card.jpg', 0, (row_i+1,col_i+1))
                    this_card.place_card()
                    row.append(this_card)
                jokers.append(row)

        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60
        time.sleep(1)

    pygame.quit()

if __name__ == "__main__":
    main()
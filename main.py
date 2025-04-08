# Main File to Call All implemented functions.

import gridwars as gw
import usb_port as usb
from card import Card
#ran python3 -m pip install -U pygame==2.6.0 
import pygame

#Sources Used: 
# https://www.pygame.org/docs/


# Defining Player Class
# class Player:
#     def __init__(self, playerNum, health, buttonPressed):
#         self.playerNum = playerNum # Personal Player Number
#         self.health = health # Total Player Health Points
#         self.buttonPressed = buttonPressed # Has Player Pressed Button (0:no or 1:yes)

#     # Function for Player Damage
#     def takeDamage(self, damage):
#         self.health -= damage

# # Lookup Table for Card Stats
# CardStats = {
#     '''ID VALUE''': {"health": 3, "power": 2, "sleep": 1}, 
#     '''ID VALUE''': {"health": 4, "power": 1, "sleep": 1}, 
#     '''ID VALUE''': {"health": 5, "power": 3, "sleep": 1}, 
#     '''ID VALUE''': {"health": 2, "power": 2, "sleep": 1}, 
#     '''ID VALUE''': {"health": 6, "power": 6, "sleep": 1}, 
#     # Keep adding more
# }

# # Defining Card Class
# class Card:
#     def __init__(self, ID):
#         self.ID = ID # Individual Card ID from RFID Scan
#         self.health = CardStats[ID]["health"] # Creature Card Health Points
#         self.power = CardStats[ID]["power"] # Creature Card Power/Attack Points
#         self.sleep = [ID]["sleep"] # Creature Card Sleep Counter (1:sleeping, 0:awake)

# Function for Actice Placement Phase
# def ActivePlacement(buttonPressed):
#     while not buttonPressed():




def main():
    pygame.init()
    screen_info = pygame.display.Info()
    screen = pygame.display.set_mode((screen_info.current_w, screen_info.current_h), pygame.FULLSCREEN) #pygame.NOFRAME for borderless window
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

    pygame.quit()

if __name__ == "__main__":
    main()
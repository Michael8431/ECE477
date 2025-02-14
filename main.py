# Main File to Call All implemented functions.

import gridwars as gw
import usb_port as usb
from card import Card
#ran python3 -m pip install -U pygame==2.6.0 
import pygame

#Sources Used: 
# https://www.pygame.org/docs/


def main():
    pygame.init()
    screen_info = pygame.display.Info()
    screen = pygame.display.set_mode((screen_info.current_w, screen_info.current_h))
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
                this_card = Card(screen, 'joker_card.jpg', 0, (row_i+1,col_i+1))
                this_card.place_card()
                row.append(this_card)
            jokers.append(row)

        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60

    pygame.quit()

if __name__ == "__main__":
    main()
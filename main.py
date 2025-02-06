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
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    running = True
    

    
    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT: #
                running = False

        # fill the screen with a color to wipe away anything from last frame
        screen.fill("purple")

        # RENDER YOUR GAME HERE
        #Create group of cards
        # p1_cards = pygame.sprite.Group() #creates group of cards for P1(bottom of screen)
        
        jokers = []
        for row_i in range(4):
            for col_i in range(6):
                this_card = Card(screen, 'joker_card.jpg', 0, (row_i+1,col_i+1))
                this_card.place_card()
                jokers.append(this_card)
        # test_card_img = pygame.image.load("joker_card.jpg").convert() #adds image from file
        # screen.blit(test_card_img, (0,0),)
        # joker1 = Card(screen, 'joker_card.jpg', 0, (1,1))
        # joker1.place_card()
        # joker2 = Card(screen, 'joker_card.jpg', 0, (1,2))
        # joker2.place_card()
        # joker3 = Card(screen, 'joker_card.jpg', 0, (1,3))
        # joker3.place_card()
        # joker4 = Card(screen, 'joker_card.jpg', 0, (1,4))
        # joker4.place_card()
        # joker5 = Card(screen, 'joker_card.jpg', 0, (1,5))
        # joker5.place_card()
        # joker6 = Card(screen, 'joker_card.jpg', 0, (2,1))
        # joker6.place_card()
        # joker7 = Card(screen, 'joker_card.jpg', 0, (3,1))
        # joker7.place_card()
        # joker8 = Card(screen, 'joker_card.jpg', 0, (4,1))
        # joker8.place_card()
        # joker3 = Card(screen, 'joker_card.jpg', 0, (1,2))
        # joker3.place_card()

        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60

    pygame.quit()

if __name__ == "__main__":
    main()
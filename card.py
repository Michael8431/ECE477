
import pygame

#Sources Used: 
# https://stackoverflow.com/questions/13851051/how-to-use-sprite-groups-in-pygame

class Card(pygame.sprite.Sprite): #Subclass of pygame.Sprite
    screen = None
    coords = [0, 0]
    def set_coords(self, slot):
        screen_x = 1280
        screen_y = 720
        card_width = 100
        card_length = 150
        row_pad = (card_width / 10)
        divider = 70
        col_pad = (150 / 7.5) * 5

        #X Coordinates
        if slot[0] == 1: #back row of P1(bottom closest row)
            self.coords[1] = row_pad #500 - 120 = 380
            # self.coords[0] = 1280 - (size_x*4)
        elif slot[0] == 2: 
            self.coords[1] = row_pad + row_pad + card_length
        elif slot[0] == 3:
            self.coords[1] = divider + row_pad + 2*(row_pad + card_length)
        elif slot[0] == 4:
            self.coords[1] = divider + row_pad + 3*(row_pad + card_length)
        #Y coordinates
        if slot[1] == 1:
            self.coords[0] = col_pad
        elif slot[1] == 2:
            self.coords[0] = col_pad + col_pad + card_width
        elif slot[1] == 3:
            self.coords[0] = col_pad + 2*(col_pad + card_width)
        elif slot[1] == 4:
            self.coords[0] = col_pad + 3*(col_pad + card_width)
        elif slot[1] == 5:
            self.coords[0] = col_pad + 4*(col_pad + card_width)
        elif slot[1] == 6:
            self.coords[0] = col_pad + 5*(col_pad + card_width)
    def __init__(self, screen, image_filename, id, slot):
        '''
        screen: pygame.display the sprite exists on
        image_filename: path and filename of the card
        id: the identification number for type of card
        slot: (x, y) where x=1-2 is P1 and 3-4 is P2,
            y=1-6 for each slot
        '''
        pygame.sprite.Sprite.__init__(self)
        #rest of class stuff goes here
        self.screen = screen
        self.set_coords(slot)
        self.image = pygame.image.load(image_filename).convert() #adds image from file
        self.image = pygame.transform.scale(self.image, (100, 150)) #Scales image to constant size
        self.rect = pygame.Rect(self.coords[0], self.coords[1], 100, 150)
    def place_card(self):
        self.screen.blit(self.image, tuple(self.coords),)
        
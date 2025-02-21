

#from runrfid import *
#	BE CAREFUL, if u import every line from a file, if it has a function call, then it autoruns
#		on bootup as that is when it is compiline every line.
from machine import Pin
from machine import Timer
from shared_variables import states_list, reading, game_state, change_state, start_read, get_state, is_change, no_change
from runrfid import runrfid
import random
import time

#states_list = ["RST", "IDLE", "ActivePlace", "ActiveRole", "PassiveDefense"]
#RST: Before Before Game starts
#		this is where it does absolutely nothing and waits for start_game
#			as everything is terminated in this phase, game wise.
#		waiting for button press of starting the game/round, switches to IDLE
#IDLE: Before Game starts
#		which player is active is decided
#			if both players do not have a role, then rng to decide who is first
#			else if both players have a role already, then swap their roles and continues to ActivePlace
#ActivePlace
#		placement phase for the active player
#		runrfid() runs here until active_end_turn_button
#		check_place_irs() runs here as well(needs to be implemented
#		upon active_end_turn, switches to ActiveRole
#ActiveRole
#		role assign phase where active player rotates cards
#		check_role_irs() still runs here, but now its only the rotation ones
#		we have location of cards placed memorized, so we only need to check the rotated irs
#			as of this phase.
#		upon active_end_turn, switches to PassiveDefense
#PassiveDefense
#		this is a re-implementation of ActivePlace but for the opposing player and does not lead into
#			a role assign phase after.
#		Passive player places cards but cannot rotate them for attacking
#		runrfid() runs here
#		check_place_irs() runs here
#		upon passive_end_turn, switches back to IDLE
#IDLE again, looping
#		Micro does not need to know what happened with the game, even if it is the end,
#			that does not effect the micro's job.

#State Machine logic

#main will be a while loop that has timer interrupts that check for
#   end turn button to change the state

player_1_role = ""
player_2_role = ""

#creating pushbutton logic
button = Pin(4, Pin.IN, Pin.PULL_UP) #Active low button on A5
# was_pressed = 0



tim_debounce = Timer(2)
def pressed(t):
    #global change_state
    # global game_state #allows other functions to see the new state value
    is_change()
    time.sleep(1)
    #if button.value():
        #change_state = 1
        #is_change()
    # else:
    #     no_change()
            
def handler(t):
    #Timer-based Interrupt/callback for debouncing
    #after switch press, check value after 100ms to avoid bouncing
    tim_debounce.init(mode=Timer.ONE_SHOT,period=120, callback=pressed)

# GPIO Interrupt for switch
# triggers on falling edge, when active low switch is pressed
button.irq(handler=handler, trigger=button.IRQ_FALLING)

#RST is basic logic, so run it up here by default then make a case for it
#   again at the end
while True:
    game_state = "RST"
    reading = False
    if get_state() == 1:
        no_change()
        game_state = "IDLE"
        break

while True:
    if game_state == "IDLE": #IDLE STATE MACHINE LOGIC
        print("IDLE State")
        #assign player to be first
        if player_1_role == "" and player_2_role == "": #Start of first round
            random_num = random.randint(0,1)
            if random_num == 0: 
                player_1_role = "Passive"
                player_2_role = "Active"
            else:
                player_1_role = "Active"
                player_2_role = "Passive"
        else: #Swap the roles
            temp = player_1_role
            player_1_role = player_2_role
            player_2_role = temp
        print("End of IDLE, Active Player's Turn")
        game_state = "ACTIVEPLACE" #going to the next
        start_read() #put it here so it doesnt infinitely start reading over and over
    elif game_state == "ACTIVEPLACE": #ACTIVEPLACE STATE MACHINE LOGIC
        #print(game_state)
        #print(get_state())
        #time.sleep(1)
        runrfid() #starts the scanner
        
        if get_state() == 1:
            no_change()
            game_state = "ACTIVEROLE"
    elif game_state == "ACTIVEROLE":
        print("ACTIVEROLE State")
        time.sleep(1)
        
        if get_state() == 1:
            no_change()
            game_state = "PASSIVEDEFENSE"
    elif game_state == "PASSIVEDEFENSE":
        print("PASSIVEDEFENSE State")
        time.sleep(1)
        
        if get_state() == 1:
            no_change()
            game_state = "IDLE"
    else:
        game_state = "RST"
        reading = False
        if get_state() == 1:
            no_change()
            game_state = "IDLE"
            
        


print("This is Main")

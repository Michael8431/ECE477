
import read
import time

#IMPORTANT#
#Run this in Thonny and keep boot.py empty as an infinite loop in boot.py bricks* the device
#boot.py is what runs when the hard reset button on the ESP32 is pressed

#read.do_read() stores the RFID tag in rdr.read(8)

#read.do_read() reads infinitely until keyboard interrupt, we will program end_rfid_scan as an interrupt
#If not working, unplug and replug

reading = True
states = ["RST", "IDLE", "ActivePlace", "ActiveRole", "PassiveDefense"]
#RST: Before Before Game starts
#		this is where it does absolutely nothing and waits for start_game
#			as everything is terminated in this phase, game wise.
#		waiting for button press of starting the game/round, switches to IDLE
#IDLE: Before Game starts
#		which player is active is decided
#			if both players do not have a role, then rng to decide who is first
#			else if both players have a role already, then swap their roles and continue to ActivePlace
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
#		upon passive_end_turn, switches back to WAIT
#IDLE again, looping
#		Micro does not need to know what happened with the game, even if it is the end,
#			that does not effect the micro's job.
game_state = "RST"
#Will implement string values for all the states so that Micro knows where we are at

def stop_read():
    global reading
    reading = False
    
def start_read():
    global reading
    reading = True
def get_reading():
    global reading
    return reading

def runrfid():
    global reading
    while True:
        read_rfid = (input("Enter 1 to run RFID scan, 0 to cancel"))
        if read_rfid == '1':
            start_read()
            print("Will read until keyboard interrupt(CTRL + C) or timeout")
            start_time = time.time()
            timeout = 10
            did_timeout = False
            print(read.do_read())
        elif read_rfid == '0':
            break
        else:
            continue
    print("Reader turning off")

runrfid()
    

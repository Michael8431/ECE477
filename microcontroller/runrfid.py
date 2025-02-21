



#IMPORTANT#
#Run this in Thonny and keep boot.py empty as an infinite loop in boot.py bricks* the device
#boot.py is what runs when the hard reset button on the ESP32 is pressed

#read.do_read() stores the RFID tag in rdr.read(8)

#read.do_read() reads infinitely until keyboard interrupt, we will program end_rfid_scan as an interrupt
#If not working, unplug and replug

#Will implement string values for all the states so that Micro knows where we are at


def runrfid():
    import read
    import time
    
    from shared_variables import get_reading, start_read, stop_read, game_state, get_state
    
    #reading = get_reading()
    #start_read()
    
    #while True:
    # read_rfid = (input("Enter 1 to run RFID scan, 0 to cancel"))
    if get_reading() == True: #if start_read() ran before this
        #start_read()
        print("Will read until keyboard interrupt(CTRL + C) or timeout")
        # start_time = time.time()
        # timeout = 10
        # did_timeout = False
        print(read.do_read())
    #elif read_rfid == '0':
        #break
    #else:
        #continue
print("Reader turning off")

# runrfid()

import read
import time

#IMPORTANT#
#Run this in Thonny and keep boot.py empty as an infinite loop in boot.py bricks* the device
#boot.py is what runs when the hard reset button on the ESP32 is pressed

#read.do_read() stores the RFID tag in rdr.read(8)

#read.do_read() reads infinitely until keyboard interrupt, we will program end_rfid_scan as an interrupt
#If not working, unplug and replug

reading = True

def stop_read():
    global reading
    reading = False
    
def start_read():
    global reading
    reading = True
def get_reading():
    global reading
    return reading

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

#while True:
    
#    time.sleep(1)
#    print(read.do_read())

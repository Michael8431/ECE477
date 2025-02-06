
import read
import time

#read.do_read() reads infinitely until keyboard interrupt, we will program end_rfid_scan as an interrupt
#If not working, unplug and replug

while True:
    read_rfid = (input("Enter 1 to run RFID scan, 0 to cancel"))
    if read_rfid == '1':
        print("Will read until keyboard interrupt(CTRL + C)")
        start_time = time.time()
        timeout = 10
        while True:
            if time.time() - start_time >= timeout:
                break
            print("Runs until keyboard interrupt")
            print(read.do_read())
        print("Timeout")
    elif read_rfid == '0':
        break
    else:
        continue
print("Reader turned off")

#while True:
    
#    time.sleep(1)
#    print(read.do_read())
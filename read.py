import mfrc522
import time #gridwards edit added by Michael to test a loop termination on timeout
from os import uname

def do_read():
	from runrfid import stop_read, start_read, get_reading #gridwars edit to enable a force stop of the reading for RFID tags --Michael
	
	if uname()[0] == 'WiPy':
		rdr = mfrc522.MFRC522("GP14", "GP16", "GP15", "GP22", "GP17")
	elif uname()[0] == 'esp32':
		rdr = mfrc522.MFRC522(5, 19, 21, 25, 7) #gridwars edit to match GPIOs of ESP32 --Michael
	else:
		raise RuntimeError("Unsupported platform")

	print("")
	print("Place card before reader to read from address 0x08")
	print("")

	try:
		start_time = time.time()
		timeout = 10
		while get_reading():
			if time.time() - start_time >= timeout:
				stop_read()
			#print(get_read_bool())
			#stop_read()
			#print(get_read_bool())
			#if stop_reading:
				#break
#gridwards edit added to force a stop to the reading of rfid values

			(stat, tag_type) = rdr.request(rdr.REQIDL)

			if stat == rdr.OK:

				(stat, raw_uid) = rdr.anticoll()

				if stat == rdr.OK:
					print("New card detected")
					print("  - tag type: 0x%02x" % tag_type)
					print("  - uid	 : 0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))
					print("")

					if rdr.select_tag(raw_uid) == rdr.OK:

						key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

						if rdr.auth(rdr.AUTHENT1A, 8, key, raw_uid) == rdr.OK:
							print("Address 8 data: %s" % rdr.read(8))
							rdr.stop_crypto1()
						else:
							print("Authentication error")
					else:
						print("Failed to select tag")

	except KeyboardInterrupt:
		print("Bye")
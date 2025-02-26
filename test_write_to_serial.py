import serial

s = serial.Serial(
    port='COM6',         
    baudrate=9600,       
    bytesize=serial.EIGHTBITS, 
    parity=serial.PARITY_NONE, 
    stopbits=serial.STOPBITS_ONE, 
    timeout=30,          
    xonxoff=False,      
    rtscts=False,        
    dsrdtr=False
)


print("Serial connection established:", s.is_open)

print(s.write(b'hello'))

s.close()
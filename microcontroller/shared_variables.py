

states_list = ["RST", "IDLE", "ACTIVEPLACE", "ACTIVEROLE", "PASSIVEDEFENSE"]

game_state = "RST" #default state

change_state = 0

def get_state():
    global change_state
    return change_state

def is_change():
    global change_state
    change_state = 1
    return change_state

def no_change():
    global change_state
    change_state = 0
    return change_state

reading = False

def stop_read():
    global reading
    reading = False
    
def start_read():
    global reading
    reading = True

def get_reading():
    global reading
    return reading
#!/usr/bin/python -u

import time
import serial
import redis

SERIAL_PORT='/dev/ttyACM0'
REDIS_HOST='localhost'
REDIS_PORT=6379

#{'status': 'CLOSED', 'motion': 'NOMOTION', 'button': 'UNPRESSED'} TEMPDISARMED
#inputs
#door sensor, motion sensor, button pressed, armed

class Sensors(object):
    def __init__(self):
        self.sensors = []
        self.debug = False
    def find(self, values):
        for value in values:
            if value not in self.sensors:
                return False
        return True
    def update_sensors(self):
        #sensors = 'OPEN:NOMOTION:UNPRESSED'.split(':')
        #sensors.append('ARMED')
        sensors = ser.readline().strip().split(':')
        sensors.append(r.get('security-mode').strip())
        if len(sensors) > 2:
            s = {"status": sensors[0], "motion": sensors[1], "button": sensors[2]}
            r.set('security-status', s)
        self.sensors = sensors
    #print self.sensors
    def check(self, values):
        return self.find(values)
    def debug_set(self, values):
        self.debug = True
        self.sensors = values

class Garage(object):
    def __init__(self):
        self.state = 'open'
        self.sensors = Sensors()
        self.timer = 0
        self.prev_state = ""
    def transition(self):
        command = r.get("command")
        if command.startswith("APPOPEN"):
            milliseconds = command.split(":")[1]
            set_disarmed()
            toggle_relay(milliseconds)
            clear_command()

        self.sensors.update_sensors()
        if self.state == "closed":
            if self.sensors.check(["OPEN", "DISARM"]):
                self.state = "open"
            elif self.sensors.check(["DISARM", "PRESSED"]):
                print "PRESSED"
                toggle_relay()
            elif self.sensors.check(["ARMED", "PRESSED"]):
                self.state = "alarming"
            elif self.sensors.check(["ARMED", "MOTION"]):
                self.state = "alarming"
            elif self.sensors.check(["ARMED", "OPEN"]):
                self.state = "alarming"
        elif self.state == "open":
            if self.sensors.check(["CLOSED"]):
                self.timer = int(time.time())
                self.state = "arming"
            elif self.sensors.check(["MOTION", "ARMED"]):
                self.state = "alarming"
            elif self.sensors.check(["PRESSED", "ARMED"]):
                self.state = "alarming"
            elif self.sensors.check(["PRESSED", "DISARM"]):
                toggle_relay()
        elif self.state == "arming":
            if self.sensors.check(["MOTION", "CLOSED"]):
                set_disarmed()
                self.state = "closed"
            elif self.timer + 15 < int(time.time()) and self.sensors.check(["CLOSED"]):
                set_armed()
                self.state = "closed"
            elif self.sensors.check(["OPEN"]):
                set_disarmed()
                self.state = "open"
            elif self.sensors.check(["PRESSED"]):
                toggle_relay()
        elif self.state == "timed_opening":
            if self.sensors.check(["DISARM"]):
                self.state = "open"
        elif self.state == "alarming":
            if self.sensors.check(["DISARM"]):
                self.state = "open"

        if self.prev_state != self.state:
            print "State changed to: {}".format(self.state)
            r.set('state', self.state)
            self.prev_state = self.state

def clear_command():
    r.set('command', "")

def set_armed():
    r.set('security-mode', "ARMED")
    print "armed"
    pass

def set_disarmed():
    r.set('security-mode', "DISARM")
    print "disarmed"
    pass

def toggle_relay(milliseconds=None):
    if milliseconds:
        ser.write("OPEN:{}!".format(milliseconds))
    else:
        ser.write("OPEN:0!")
    print "relay toggled"
    pass

if __name__ == "__main__":
    garage = Garage()
    prev_state = ""
    ser = serial.Serial(SERIAL_PORT, 9600, timeout=5)
    ser.flushInput()
    r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    while True:
        garage.transition()
        if garage.state != prev_state:
            print garage.state
        prev_state = garage.state
    pass

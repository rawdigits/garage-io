#!/usr/bin/python

import serial
import redis
import pynma
import time
import os

from config import *
from shared import *

wait_for_redis()

ser = serial.Serial(SERIAL_PORT,9600,timeout=5)
r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
p = pynma.PyNMA( r.get('prowl-api-key') )
ser.flushInput()

def send_message(message):
  try:
    p.push("GARAGE","GARAGE",message)
  except:
    pass

class Alerter:
  def __init__(self):
    self.last_alert = 0

  def alert(self, message):
    if time.time() > (self.last_alert + 10):
      for i in range(1,5):
        send_message(message)
        time.sleep(.5)
        os.system('/usr/bin/aplay /home/pi/alarm.wav')
      ser.flushInput()
      self.last_alert = time.time()

alerter = Alerter()

def toggle_relay(now = None):
  if now:
    ser.write("OPEN:0" + "!")
    time.sleep(1)
  else:
    command = r.get('command')
    print "%s : %s" % (time.asctime(), command)
    if command != None and command[0:4] == "OPEN":
      ser.write(command + "!")
      r.set('command','')
      time.sleep(.5)
      ser.flushInput()

def check_sensors():
  try:
    state_in = ser.readline().strip().split(':')
    state = {"status":state_in[0], "motion":state_in[1], "button":state_in[2]}
  except:
    state = {"status":"CLOSED", "motion":"NOMOTION", "button":"UNPRESSED"}
  hard_button.monitor(state["button"])
  r.set('security-status', "%s" % (state))
  return state

def check_mode():
  try:
    mode = r.get('security-mode').strip()
  except:
    mode = "ARMED"
  return mode

class Button:
  def __init__(self):
    self.last_state = ""
    self.checked = True
  def check(self):
    print "called check, checked: %s" % (self.checked)
    if self.checked == False:
      self.checked = True
      return True
    else:
      return False
  def monitor(self, state):
    if state != self.last_state and state == "PRESSED":
      self.checked = False
    self.last_state = state

hard_button = Button()


#YES I KNOW THIS NEEDS TO BECOME A STATE MACHINE
while True:
  state = check_sensors()
  toggle_relay()
  mode = check_mode()
  #This allows a TEMP DISARM mode, which means disable until we are 'CLOSED' again
  if mode == 'TEMPDISARMED':
    if hard_button.check():
      toggle_relay(True)
    if state["status"] == 'OPEN':
      while True:
        if hard_button.check():
          toggle_relay(True)
        state = check_sensors()
        toggle_relay()
        #allows you to arm motion sensor without closing door and disarm to break the loop
        mode = check_mode()
        if mode == "ARMED" and state["motion"] == "MOTION":
          alerter.alert("%s" % (state))
        elif mode == "DISARM":
          break
        if state["status"] == 'CLOSED':
          send_message("Door Closed")
          #First if we see movement someone is presumably inside intentionally
          security_mode = "ARMED"
          closed_time = time.time()
          while time.time() < closed_time + 15:
            state = check_sensors()
            if state["motion"] == "MOTION":
              security_mode = "TEMPDISARMED"
          #Otherwise arm the system
          r.set('security-mode', security_mode)
          send_message(security_mode)
          break
    else:
      continue

  if (state["status"] != 'CLOSED' or state["motion"] == 'MOTION') and mode == 'ARMED':
    alerter.alert("%s" % (state))
  elif mode == 'TEST':
    r.set('security-mode', '')
    alerter.alert("%s" % (state))
  else:
    #this below line makes sure a tempdisarm doesn't open the door accidentally
    hard_button.check()


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

def toggle_relay():
  command = r.get('command')
  print "%s : %s" % (Time.asctime(), command)
  if command != None and command[0:4] == "OPEN":
    ser.write(command + "!")
    r.set('command','')
    time.sleep(.5)
    ser.flushInput()

def check_sensors():
  try:
    status,motion = ser.readline().strip().split(':')
  except:
    status,motion = "CLOSED","NOMOTION"
  r.set('security-status', "%s %s" % (status, motion))
  return status,motion

def check_mode():
  try:
    mode = r.get('security-mode').strip()
  except:
    mode = "ARMED"
  return mode
  

#YES I KNOW THIS NEEDS TO BECOME A STATE MACHINE
while True:
  status,motion = check_sensors()
  toggle_relay()
  mode = check_mode()
  #This allows a TEMP DISARM mode, which means disable until we are 'CLOSED' again
  if mode == 'TEMPDISARMED':
    if status == 'OPEN':
      while True:
        status, motion = check_sensors()
        toggle_relay()
        #allows you to arm motion sensor without closing door and disarm to break the loop
        mode = check_mode()
        if mode == "ARMED" and motion == "MOTION":
          alerter.alert("%s %s" % (status, motion))
        elif mode == "DISARM":
          break
        if status == 'CLOSED':
          send_message("Door Closed")
          #First if we see movement someone is presumably inside intentionally
          security_mode = "ARMED"
          closed_time = time.time()
          while time.time() < closed_time + 15:
            status, motion = check_sensors()
            if motion == "MOTION":
              security_mode = "TEMPDISARMED"
          #Otherwise arm the system
          r.set('security-mode', security_mode)
          send_message(security_mode)
          break
    else:
      continue

  if (status != 'CLOSED' or motion == 'MOTION') and mode == 'ARMED':
    alerter.alert("%s %s" % (status, motion))
  elif mode == 'TEST':
    r.set('security-mode', '')
    alerter.alert("%s %s" % (status, motion))

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

class Alerter:
  def __init__(self):
    self.last_alert = 0

  def alert(self, message):
    if time.time() > (self.last_alert + 10):
      for i in range(1,5):
        p.push("GARAGE","GARAGE",message)
        time.sleep(.5)
        os.system('/usr/bin/aplay /home/pi/alarm.wav')
      ser.flushInput()
      self.last_alert = time.time()

alerter = Alerter()

def toggle_relay():
  command = r.get('command')
  if command != None and command[0:4] == "OPEN":
    ser.write(command + "!")
    r.set('command','')
    time.sleep(.5)
    ser.flushInput()

while True:
  try:
    status,motion = ser.readline().strip().split(':')
  except:
    status,motion = "CLOSED","NOMOTION"
  mode = r.get('security-mode')
  toggle_relay()
  r.set('security-status', "%s %s" % (status, motion))
  #This allows a TEMP DISARM mode, which means disable until we are 'CLOSED' again
  if mode == 'TEMPDISARMED':
    if status == 'OPEN':
      while True:
        status, motion = ser.readline().strip().split(':')
        toggle_relay()
        r.set('security-status', "%s %s" % (status, motion))
        if r.get('security-mode').strip() == "ARMED" and motion == "MOTION":
          alerter.alert("%s %s" % (status, motion))
        if status == 'CLOSED':
          r.set('security-mode', 'ARMED')
          p.push("GARAGE","GARAGE","REARMED")
          break

  if (status != 'CLOSED' or motion == 'MOTION') and mode == 'ARMED':
    alerter.alert("%s %s" % (status, motion))
  elif mode == 'TEST':
    r.set('security-mode', '')
    alerter.alert("%s %s" % (status, motion))

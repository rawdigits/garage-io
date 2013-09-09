#!/usr/bin/python


import serial

ser = serial.Serial('/dev/ttyACM0',9600,timeout=5)

ser.flushInput()

while True:
  status = ser.readline().strip()
  print status

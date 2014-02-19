garage-io
=========

NOW BATTLE TESTED! (see below)
Garage control and monitoring system. Uses Arduino > serial > python.  

Currently sends push notification via Prowl for iOS and plays alarm sound via Raspberry PI headphone jack.

## Example usage:

    http://raspi.example.com:8080/status
    
    http://raspi.example.com:8080/mode/(ARMED/DISARMED/TEMPDISARMED)
    
    http://raspi.example.com:8080/command/OPEN[:2000] #optional milliseconds to trigger relay a second time







## Dependencies:

pySerial  
redis-py  
bottle.py  

## Optional:
PyNMA

##This guy opened my garage at 4am, thanks to garage-io he got zero things:
![Jerk](https://dl.dropboxusercontent.com/u/566560/208-capture.jpg)

## Questionably alpha hardware:
![Version 1](https://dl.dropboxusercontent.com/u/566560/garage-security.jpg)

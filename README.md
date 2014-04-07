garage-io
=========

NOW BATTLE TESTED! (see below)
Garage control and monitoring system. Uses Arduino > serial > python.  

Currently sends push notification via Prowl for iOS and plays alarm sound via Raspberry PI headphone jack.

## Example usage:

    http://raspi.example.com:8080/status
    
    http://raspi.example.com:8080/mode/(ARMED/DISARMED/TEMPDISARMED)
    
    http://raspi.example.com:8080/command/OPEN[:2000] #optional milliseconds to trigger relay a second time

#Parts List
### Physical Dependencies (parts list):

Name|purpose|source
--------|:--------|:--------
Raspberry Pi Model B|Runs client software, master controller|http://www.adafruit.com/products/998
Arduino|Monitors sensors, triggers relays|http://www.adafruit.com/products/50
SainSmart 2-Channel Relay Module|for opening and closing doors|http://www.amazon.com/dp/B0057OC6D8/ref=pe_385040_30332190_pe_175190_21431760_M3T1_ST1_dp_1
Magnetic Door sensors|detect door open/closed|http://www.amazon.com/gp/product/B0009SUF08/ref=oh_details_o09_s00_i02?ie=UTF8&psc=1
Passive Infrared (PIR) Motion Sensor|for detecting movement|http://www.adafruit.com/products/189
Handy connecting cables M-to-F|useful for quick bridging stuff to raspi/arduino|http://www.amazon.com/gp/product/B00A6SOGC4/ref=oh_details_o05_s00_i00?ie=UTF8&psc=1
Short usb cable|for connecting Arduino to Pi |http://www.amazon.com/gp/product/B00004Z5IE/ref=oh_details_o06_s00_i01?ie=UTF8&psc=1
Small gauge wire|for wiring to sensors|Radioshack/wherever


### Optional parts:

Name|purpose|source
--------|:--------|:--------
Wifi dongle|for make wireless|http://www.amazon.com/gp/product/B002VJL0OI/ref=oh_details_o03_s00_i00?ie=UTF8&psc=1
USB to TTL Serial Cable|lets you connect to RasPI serial console|http://www.adafruit.com/products/954


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

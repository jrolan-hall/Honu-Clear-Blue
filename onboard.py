import explorerhat as eh
from random import random
import time
from datetime import datetime
from math import atan2, pi, asin, cos, sqrt
import Adafruit_LSM303

#lsm303 = Adafruit_LSM303.LSM303()

def output():
	return str(random())

def sense_DATA():
	packet = {}

	packet["MSG"] = "DATA"
	packet["DATE"] = datetime.utcnow().strftime("%Y-%b-%d")
	packet["TIME"] = datetime.utcnow().strftime("%I:%M:%S %p")

	#CONTROL
	#if eh.touch.is_pressed()["one"]==True and eh.touch.is_pressed()["two"]==True and  eh.touch.is_pressed()["three"]==True:
	#	packet["CTRL"] = "M"
	#else:
	#	packet["CTRL"] = "A"


	#FRONT CLEARANCE
	#IR sensor
	F_in = eh.analog.one.read()
	if F_in < 0.4: 
		packet['FCLR'] = 'N'	#clear
		packet['FDIST'] = ' ' + u"\u221E" + ' '
	else:
		packet['FCLR'] = '1'	#obstacle nearby
		packet['FDIST'] = str(round((17/10.0 - F_in/2.0),3))

	#Touch sensor
	if eh.input.one.read()==True:
		packet['FCLR'] = '2'	#collision
		packet['FDIST'] = 0


	#LEFT CLEARANCE
	if eh.touch.is_pressed()["one"]==True and eh.touch.is_pressed()["four"]==True:
		packet["LCLR"]="1" #<35cm = True
	elif eh.touch.is_pressed()["one"]==True and eh.touch.is_pressed()["five"]==True:
		packet["LCLR"]="2" #limit switch hit
	else:
		packet["LCLR"]="N" #clear

	#RIGHT CLEARANCE
	if eh.touch.is_pressed()["one"]==True and eh.touch.is_pressed()["six"]==True:
		packet["RCLR"]="1" #<35cm = True
	elif eh.touch.is_pressed()["one"]==True and eh.touch.is_pressed()["seven"]==True:
		packet["RCLR"]="2" #limit switch hit
	else:
		packet["RCLR"]="N" #clear


	#BACK CLEARANCE
	#IR sensor
	B_in = eh.analog.two.read()
	if B_in < 0.4: 
		packet['BCLR'] = 'N'	#clear
		packet['BDIST'] = ' ' + u"\u221E" + ' '
	else:
		packet['BCLR'] = '1'	#obstacle nearby
		packet['BDIST'] = str(round((17/10.0 - B_in/2.0),3))

	#Touch sensor
	if eh.input.four.read()==True:
		packet['BCLR'] = '2'	#collision
		packet['BDIST'] = 0

	#DOOR STATE
	#if eh.touch.is_pressed()["three"]==True and eh.touch.is_pressed()["five"]==True:
	#	packet["DOOR"]="O" #opening
	#elif eh.touch.is_pressed()["three"]==True and eh.touch.is_pressed()["six"]==True:
	#	packet["DOOR"]="C" #closing
	#else:
	#	packet["DOOR"]="N" #neutral

	#INDICATOR STATE
	if eh.touch.is_pressed()["three"]==True and eh.touch.is_pressed()["seven"]==True:
		packet["INDI"]="1" #indicator 1
	elif eh.touch.is_pressed()["three"]==True and eh.touch.is_pressed()["eight"]==True:
		packet["INDI"]="2" #indicator 2
	else:
		packet["INDI"]="N" #neutral

	#VOLUME
	if eh.touch.is_pressed()["four"]==True and eh.touch.is_pressed()["five"]==True:
		packet["VOL"]="M" #medium
	elif eh.touch.is_pressed()["four"]==True and eh.touch.is_pressed()["six"]==True:
		packet["VOL"]="F" #full
	else:
		packet["VOL"]="E" #empty

	#BATTERY
	if eh.touch.is_pressed()["four"]==True and eh.touch.is_pressed()["seven"]==True:
		packet["BAT"]="M" #medium
		packet["BATL"] = "50"
	elif eh.touch.is_pressed()["four"]==True and eh.touch.is_pressed()["eight"]==True:
		packet["BAT"]="F" #full
		packet["BATL"] = "100"
	else:
		packet["BAT"]="E" #empty
		packet["BATL"] = "00"

	#COMB TORQUE
	if eh.touch.is_pressed()["five"]==True and eh.touch.is_pressed()["six"]==True:
		packet["CMB"]="M" #medium
	elif eh.touch.is_pressed()["five"]==True and eh.touch.is_pressed()["seven"]==True:
		packet["CMB"]="H" #HIGH
	else:
		packet["CMB"]="N" #normal

	#SPEED
	if eh.touch.is_pressed()["five"]==True and eh.touch.is_pressed()["eight"]==True:
		packet["SPD"]=str(10*random())[:3] #random number between 0 and 10
	else:
		packet["SPD"]="00" #dummy

	#HUMIDITY
	if eh.touch.is_pressed()["six"]==True and eh.touch.is_pressed()["seven"]==True:
		packet["HUM"]=str(100*random())[:3] #random number between 0 and 100
	else:
		packet["HUM"]="00" #dummy

	#TEMPERATURE
	if eh.touch.is_pressed()["six"]==True and eh.touch.is_pressed()["eight"]==True:
		packet["TMP"]=str(20+10*random())[:3] #random number between 20 and 30
	else:
		packet["TMP"]="00" #dummy

	#BEARING
	"""
	accel, mag = lsm303.read()
	accel_x, accel_y, accel_z = accel
	mag_x, mag_z, mag_y = mag
	Axn = accel_x/sqrt(accel_x**2 + accel_y**2 + accel_z**2)
	Ayn = accel_y/sqrt(accel_x**2 + accel_y**2 + accel_z**2)
	pitch = asin(-Axn)
	roll = asin(Ayn/cos(pitch))
	"""
	packet['PITCH'] = 1#pitch*180/pi
	packet['ROLL'] = 1#roll*180/pi
	packet['BEAR'] = 1#180*atan2(mag_y, mag_x)/pi	#calculate bearing	
	
	
	#ALTITUDE, LATITUDE, LONGITUDE
	packet["ALT"] = str(random()*1000)[:3]
	packet["LAT"] = str(round(random()*90,7))[:8]
	packet["LON"] = str(round(random()*180,7))[:8]

	#NODES
	visited = int(random()*100)
	packet["VNODE"] = str(visited)[:3]
	packet["RNODE"] = str(100-visited)[:3]


	#SAVE
	#if count%20 == 0:
		#write_out('\n'+str(packet))

	return (packet)

def write_out(string):
	output = open("./logs/blackbox.txt", "a")
	output.write(string)
	output.close()

def inalert1():
	eh.light.blue.on()

def inalert2():
	eh.light.blue.off()

def connalert1():
	eh.light.red.on()

def connalert2():
	eh.light.red.off()

def outalert1():
	eh.light.yellow.on()

def outalert2():
	eh.light.yellow.off()

def waitalert1():
	eh.light.green.on()

def waitalert2():
	eh.light.green.off()

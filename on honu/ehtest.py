import explorerhat as eh
from time import sleep
from random import random


dict = {}

while True:
	#FRONT CLEARANCE
	if eh.touch.is_pressed()['one']==True and eh.touch.is_pressed()['two']==True:
		dict['FCLR']=str(40+20*random())[:3] #some number between 40 and 80
	elif eh.touch.is_pressed()['one']==True and eh.touch.is_pressed()['three']==True:
		dict['FCLR']=str(20*random())[:3] #some number between 0 and 40
	else:
		dict['FCLR']=str(80.0) #clear

	#LEFT CLEARANCE
	if eh.touch.is_pressed()['one']==True and eh.touch.is_pressed()['four']==True:
		dict['LCLR']='1' #<35cm = True
	elif eh.touch.is_pressed()['one']==True and eh.touch.is_pressed()['five']==True:
		dict['LCLR']='2' #limit switch hit
	else:
		dict['LCLR']='N' #clear

	#RIGHT CLEARANCE
	if eh.touch.is_pressed()['one']==True and eh.touch.is_pressed()['six']==True:
		dict['RCLR']='1' #<35cm = True
	elif eh.touch.is_pressed()['one']==True and eh.touch.is_pressed()['seven']==True:
		dict['RCLR']='2' #limit switch hit
	else:
		dict['RCLR']='N' #clear

	#BACK CLEARANCE
	if eh.touch.is_pressed()['one']==True and eh.touch.is_pressed()['eight']==True:
		dict['BCLR']='1' #<35cm = True
	elif eh.touch.is_pressed()['two']==True and eh.touch.is_pressed()['three']==True:
		dict['BCLR']='2' #limit switch hit
	else:
		dict['BCLR']='N' #clear

	#COMB MOTOR
	if eh.touch.is_pressed()['two']==True and eh.touch.is_pressed()['four']==True:
		dict['CMO']='F' #forward
	elif eh.touch.is_pressed()['two']==True and eh.touch.is_pressed()['five']==True:
		dict['CMO']='R' #reverse
	else:
		dict['CMO']='N' #neutral

	#LEFT MOTOR
	if eh.touch.is_pressed()['two']==True and eh.touch.is_pressed()['six']==True:
		dict['LMO']='F' #forward
	elif eh.touch.is_pressed()['two']==True and eh.touch.is_pressed()['seven']==True:
		dict['LMO']='R' #reverse
	else:
		dict['LMO']='N' #neutral

	#RIGHT MOTOR
	if eh.touch.is_pressed()['two']==True and eh.touch.is_pressed()['eight']==True:
		dict['RMO']='F' #forward
	elif eh.touch.is_pressed()['three']==True and eh.touch.is_pressed()['four']==True:
		dict['RMO']='R' #reverse
	else:
		dict['RMO']='N' #neutral

	#DOOR STATE
	if eh.touch.is_pressed()['three']==True and eh.touch.is_pressed()['five']==True:
		dict['DOOR']='O' #opening
	elif eh.touch.is_pressed()['three']==True and eh.touch.is_pressed()['six']==True:
		dict['DOOR']='C' #closing
	else:
		dict['DOOR']='N' #neutral

	#INDICATOR STATE
	if eh.touch.is_pressed()['three']==True and eh.touch.is_pressed()['seven']==True:
		dict['INDI']='1' #indicator 1
	elif eh.touch.is_pressed()['three']==True and eh.touch.is_pressed()['eight']==True:
		dict['INDI']='2' #indicator 2
	else:
		dict['INDI']='N' #neutral

	#VOLUME
	if eh.touch.is_pressed()['four']==True and eh.touch.is_pressed()['five']==True:
		dict['VOL']='M' #medium
	elif eh.touch.is_pressed()['four']==True and eh.touch.is_pressed()['six']==True:
		dict['VOL']='F' #full
	else:
		dict['VOL']='E' #empty

	#BATTERY
	if eh.touch.is_pressed()['four']==True and eh.touch.is_pressed()['seven']==True:
		dict['BAT']='M' #medium
	elif eh.touch.is_pressed()['four']==True and eh.touch.is_pressed()['eight']==True:
		dict['BAT']='F' #full
	else:
		dict['BAT']='E' #empty

	#COMB TORQUE
	if eh.touch.is_pressed()['five']==True and eh.touch.is_pressed()['six']==True:
		dict['CMB']='M' #medium
	elif eh.touch.is_pressed()['five']==True and eh.touch.is_pressed()['seven']==True:
		dict['CMB']='H' #HIGH
	else:
		dict['CMB']='N' #normal

	#SPEED
	if eh.touch.is_pressed()['five']==True and eh.touch.is_pressed()['eight']==True:
		dict['SPD']=str(10*random())[:3] #random number between 0 and 10
	else:
		dict['SPD']='00' #dummy

	#HUMIDITY
	if eh.touch.is_pressed()['six']==True and eh.touch.is_pressed()['seven']==True:
		dict['HUM']=str(100*random())[:3] #random number between 0 and 100
	else:
		dict['HUM']='00' #dummy

	#TEMPERATURE
	if eh.touch.is_pressed()['six']==True and eh.touch.is_pressed()['eight']==True:
		dict['TMP']=str(20+10*random())[:3] #random number between 20 and 30
	else:
		dict['TMP']='00' #dummy

	#BEARING
	if eh.touch.is_pressed()['seven']==True and eh.touch.is_pressed()['eight']==True:
		dict['BEAR']=str(180*random())[:3] #random number between 0 and 180
	else:
		dict['BEAR']='00' #dummy

	print '\n'
	print dict

	sleep(2)


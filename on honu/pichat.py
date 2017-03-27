import network
import sys
from random import random
import onboard
import evdev
import threading


class App():
    def __init__(self):

		def heard(phrase):
			onboard.inalert1()
			print "INCOMING:" + phrase
			onboard.inalert2()
			if network.isConnected():
				if phrase == 'DATA':
					response = onboard.sense_DATA()
					onboard.outalert1()
					print"RESPONSE:" + str(response)
					try:
						network.say(str(response))
					except:
						print 'could not send message'
					onboard.outalert2()
		  		else:
		  			print"NO CONNECTION TO RESPOND"


		def scale(val, src, dst):
		    """
		    Scale the given value from the scale of src to the scale of dst.

		    val: float or int
		    src: tuple
		    dst: tuple

		    example: print(scale(99, (0.0, 99.0), (-1.0, +1.0)))
		    """
		    return (float(val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0]

		def scale_stick(value):
		    return scale(value,(0,255),(-1,1))

		def scale_trigger(value):
		    return int(scale(value,(0,255),(0,100)))

		def control_wait():
		    print 'Awaiting controller connection'
		    self.gamepad = None
		    while self.gamepad == None:
		        devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
		        for device in devices:
		            if device.name == 'PLAYSTATION(R)3 Controller':
		                ps3dev = device.fn
		                self.gamepad = evdev.InputDevice(ps3dev)
		                print 'Controller connection made'

		def define_allkeys():
		    self.allkeys = { #control name: [event type, event code]
		      'CROSS_btn': [1, 302],	#cross button
		      'TRIAN_btn': [1, 300],	#triangle button
		      'CIRCL_btn': [1, 301],	#circle button
		      'SQUAR_btn': [1, 303],	#square button
		      'LEFTA_btn': [1, 295],	#left arrow button
		      'RIGHT_btn': [1, 293],	#right arrow button
		      'UPARR_btn': [1, 292],	#up arrow button
		      'DOWNA_btn': [1, 294],	#down arrow button
		      'SELCT_btn': [1, 288],	#select button
		      'START_btn': [1, 291],	#start button
		      'LEFT1_btn': [1, 298],	#L1 button
		      'LEFT2_btn': [1, 296],	#L2 button
		      'RIHT1_btn': [1, 299],	#R1 button
		      'RIHT2_btn': [1, 297],	#R2 button
		      'LSTCK_btn': [1, 289],	#left stick button
		      'RSTCK_btn': [1, 290],	#right stick button
		      'LEFTY_stk': [3, 1],	#left joystick y-axis
		      'RIHTY_stk': [3, 5],	#right joystick y-axis
		      'LEFTX_stk': [3, 0],	#left joystick x-axis
		      'RIHTX_stk': [3, 2],	#right joystick x-axis
		      'LEFT1_trg': [3, 50],	#L1 trigger
		      'LEFT2_trg': [3, 48],	#L2 trigger
		      'RIHT1_trg': [3, 51],	#R1 trigger
		      'RIHT2_trg': [3, 49]	#R2 trigger
		      #'XAXIS_acc': [3, 59],	#x-axis accelerometer
		      #'YAXIS_acc': [3, 60]	#y-axis accelerometer
		      }

		    self.command = 'CMO:0||LMO:0||RMO:0||DOOR:0'		

		def pass_command():
			acc = scale_trigger(self.keyval['RIHT2_trg'])-scale_trigger(self.keyval['LEFT2_trg'])
			turn = scale_stick(self.keyval['LEFTX_stk'])
			pivot = self.keyval['SQUAR_btn']

			#sensitivity threshold of 15% kept both motors turning okay
			if (abs(turn)>0.15) and (pivot==0): #no pivot turn - 1 wheel stationary
				if turn < 0: #left turn - right motor fwd/rev, left motor stationary
					l_acc = 0
					r_acc = int(acc*-1*turn)
				elif turn > 0: #right turn - right motor fwd/rev, right motor stationary
					r_acc = 0
					l_acc = int(acc*turn)
			elif (abs(turn)>0.15) and (pivot!=0):
				if turn < 0: #left turn - right motor fwd/rev, left motor oppose
					l_acc = int(turn*acc)
					r_acc = int(-1*turn*acc)
				elif turn > 0: #right turn - left motor fwd/rev, right motor oppose
					r_acc = int(turn*-1*acc)
					l_acc = int(turn*acc)
			else: #no turn
				l_acc = acc
				r_acc = acc

			string = 'CMO:0||'+'LMO:'+str(l_acc)+'||RMO:'+str(r_acc)+'||DOOR:0'
			if string != self.command:
				self.command = string
				print self.command

		def control():
		    control_wait()
		    define_allkeys()
		    self.keyval = {} #key values
		    for key in self.allkeys:
		    	self.keyval[key] = 0 #initialize all values to zero

		    try:
				for event in self.gamepad.read_loop():
					for key in self.allkeys:
						[etype, ecode] = self.allkeys[key]
						if event.type == etype and event.code == ecode:
							self.keyval[key] = event.value
					pass_command()
		    except:
				pass

	   	############ this is where the program starts its loop
	    			

		t = threading.Thread(target=control)# need to work on this some more
		t.start()

		print 'Awaiting network connection'
		onboard.waitalert1()
		network.wait(whenHearCall=heard)
		print 'Network connection made' 
		onboard.waitalert2()
		onboard.connalert1()
		while True:
			while network.isConnected():
				talk = True
			if network.isConnected()==False:
				onboard.connalert2()
				print 'Disconnected. Waiting for connection'
				network.hangUp()
				onboard.waitalert1()
				network.wait(whenHearCall=heard)
				print "Connection made"
				onboard.waitalert2()
				onboard.connalert1()

app=App()
import network
import onboard
import evdev
import threading
from time import sleep, time
import explorerhat as eh
import serial
from select import select

arduino = serial.Serial('/dev/ttyACM0', 9600)


class App():
    def __init__(self):

		def heard(phrase):
			onboard.inalert1() #remove with eh
			print "INCOMING:" + phrase
			words = str(phrase)
			self.homemsg = eval(words)			
			onboard.inalert2()

			if network.isConnected():
				if self.homemsg['MSG'] == 'DATA':
					if self.data_loop == False:
						self.data_loop = True
						def data_loop():
							while True:
								if network.isConnected():
									onboard.outalert1()
									response = self.state
									#print"RESPONSE:" + str(response)
									try:
										network.say(str(response))
										#print response
									except:
										pass
										#print 'could not send message'
									onboard.outalert2()
									sleep(0.1)
								else:
									pass
									#print 'no home connection'
						x = threading.Thread(target=data_loop)
						x.start()
				elif self.homemsg['MSG'] == 'SER':
				    arduino.write(self.homemsg['CMD'])
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
			if self.keyval['START_btn']==True: #manual mode
				self.control = 'M'
				print 'M control'

			if self.keyval['SELCT_btn']==True: #auto mode
				self.control = 'A'
				print 'A control'

			if self.keyval['CIRCL_btn']==True: #lock motors
				sleep(0.012)
				arduino.write('6000\n')
				self.l_acc = 0
				self.r_acc = 0
				self.c_acc = 0
				self.acc = 0
				print 'Locked'

			if self.keyval['TRIAN_btn']==True: #door open - drive motors stop to do this
				#sleep(0.012)
				arduino.write('1500\n')
				#sleep(0.012)
				arduino.write('5999\n')
				self.door = 'O'
				self.acc = 0
				print 'door open'

			if self.keyval['SQUAR_btn']==True: #door close - drive motors stop to do this
				#sleep(0.012)
				arduino.write('1500\n')
				#sleep(0.012)
				arduino.write('5000\n')
				self.door = 'C'
				self.acc = 0
				print 'door close'

			if self.keyval['UPARR_btn']==True: #comb on
				#sleep(0.012)
				arduino.write('4350\n')
				self.c_acc = 1
				print 'comb on'

			if self.keyval['DOWNA_btn']==True: #comb off
				#sleep(0.012)
				arduino.write('4500\n')
				self.c_acc = 0
				print 'comb off'

			self.pivot = self.keyval['CROSS_btn']

			if (self.keyval['RIHT1_btn']==True) and (self.acc>-101):
				print 'rev'
				self.acc += -0.33
			if (self.keyval['LEFT1_btn']==True) and (self.acc<101):
				self.acc += 0.33
				print 'fwd'
			if int(self.acc)%10 == 0:
				print int(self.acc)

			#self.acc = scale_trigger(self.keyval['LEFT2_trg'])-scale_trigger(self.keyval['RIHT2_trg'])

			self.turn = 0

			if self.keyval['RIGHT_btn']==True:
				self.turn = 1 #right
				print 'right turn'

			if self.keyval['LEFTA_btn']==True:
				self.turn = -1 #left
				print 'left turn'
			if (self.keyval['RIGHT_btn']==True) and (self.keyval['LEFTA_btn']==True):
				self.turn = 0
               	        output = int(1500-500*self.acc/100.0)
               	        if output > 1999:
               	            output = 1999
               	        if (self.acc != 0) and (self.turn == 0) and (int(self.acc)%10 == 0): #forward and backwards at same speed
               	            arduino.write(str(output)+'\n')
               	            print 'drive: '+str(output)
               	            self.l_acc = self.acc
               	            self.r_acc = self.acc
               	        elif (self.acc != 0) and (self.turn != 0) and (self.pivot == False):
               	            if (output != 1500):
               	                if self.turn > 0: #right turn - left wheel moves, right wheel stops
               	                    print 'right turn'
               	                    arduino.write('3500\n')
               	                    self.r_acc = 0
               	                    self.l_acc = self.acc
               	                elif self.turn < 0: #left turn - right wheel moves, left wheel stops
               	                    print 'left turn'
               	                    arduino.write('2500\n')
               	                    self.l_acc = 0
               	                    self.r_acc = self.acc
               	        elif (self.acc != 0) and (self.turn != 0) and (self.pivot == True):
               	            if (output != 1500):
               	                if self.turn > 0: #right turn - left wheel moves, right wheel reverse
               	                    print 'right pivot'
               	                    r_out = 3500 + (output - 1500)
               	                    arduino.write(str(r_out)+'\n')
               	                    self.l_acc = self.acc
               	                    self.r_acc = -self.acc
               	                elif self.turn < 0: #left turn - right wheel moves, left wheel reverse
               	                    print 'left pivot'
               	                    l_out = 2500 - (output - 1500)
               	                    arduino.write(str(l_out)+'\n')
               	                    self.r_acc = self.acc
               	                    self.l_acc = -self.acc
               	        else:
               	            print 'unknown state'
               	            #arduino.write('1500\n')



		def hello_arduino():
			howdy = arduino.readline()
			#print howdy
			try:
				howdy = howdy[:-1].split(':')
				tag = howdy[0]
				value = howdy[1]
			except:
				tag = None
				value = None
			if tag == 'SIR1':
				if int(value) > 2:
					self.state['VOL'] = 1
			elif tag == 'SIR2':
				if int(value) > 2:
					self.state['VOL'] = 2
			elif tag == 'SIR3':
				if int(value) > 2:
					self.state['VOL'] = 3
			elif tag == 'DSW':
				if int(value) == 1:
				    self.state['DOOR'] = 'N'
			elif tag == 'FCLF':
				self.state['FCLIFF'] = value
			elif tag == 'BCLF':
				self.state['BCLIFF'] = value
			elif tag == 'HMD':
				self.state['HUM'] = value
			elif tag == 'TMP':
				self.state['TMP'] = value

			'''
			hail = hail[:-2].split('|')
			[HMD_str, TMP_str, DSW_str, SIR1_str, SIR2_str, SIR3_str, LCLIFF_str, R_CLIFF_str, BATL_str] = [0,0,0,0,0,0,0,0,0]
			strings = [HMD_str, TMP_str, DSW_str, SIR1_str, SIR2_str, SIR3_str, LCLIFF_str, R_CLIFF_str, BATL_str] 
			if len(hail)==len(strings):
				for i in range(0, len(strings)):
					strings[i] = (hail[i]).split(':')[1]
				self.state['HUM'] = HMD_str
				self.state['TMP'] = TMP_str

				#check door
				if int(DSW_str) == 1: #door is closed
					self.state['DOOR'] = 'N'

				#check receptacle
				level = 0
				shell_IRs = [SIR1_str, SIR2_str, SIR3_str]
				for IR in shell_IRs:
					if int(IR) == 1:
						level += 1
				self.state['VOL'] = level
				self.state['LCLIFF'] = LCLIFF_str
				self.state['RCLIFF'] = R_CLIFF_str
				self.state['BATL'] = BATL_str
			'''

			#tell_arduino()



		def set_defaults():
			self.door = 'C' #trash door: N = neutral (closed), C = closing, O1 = opening, O = neutral(open)
			self.control = 'M' #control type: A = auto, M = manual
			self.c_acc = 0 #comb acceleration
			self.l_acc = 0
			self.r_acc = 0
			self.acc = 0
			self.obl = False

			#ready to connect light show
			set_all_LED_color('G')

			def get_state():
				while True:
					self.state = onboard.sense_DATA()
					self.state['CACC'] = self.c_acc
					self.state['LACC'] = self.l_acc
					self.state['RACC'] = self.r_acc
					self.state['DOOR'] = self.door
					self.state['FLED'] = self.F_LED
					self.state['LLED'] = self.L_LED
					self.state['RLED'] = self.R_LED
					self.state['BLED'] = self.B_LED
					self.state['CTRL'] = self.control
					if self.l_acc > 0:
						self.state['LMO'] = 'F'
					elif self.l_acc < 0:
						self.state['LMO'] = 'R'
					else:
						self.state['LMO'] = 'N'
					if self.r_acc > 0:
						self.state['RMO'] = 'F'
					elif self.r_acc < 0:
						self.state['RMO'] = 'R'
					else:
						self.state['RMO'] = 'N'
					if self.c_acc > 0:
						self.state['CMO'] = 'F'
					elif self.c_acc < 0:
						self.state['CMO'] = 'R'
					else:
						self.state['CMO'] = 'N'
					hello_arduino()
					sleep(0.02)
					#collision_avoidance()
					#print self.state['FDIST'], self.state['FCLR'], self.state['BDIST'], self.state['BCLR']

			u = threading.Thread(target=get_state)# need to work on this some more
			u.start()

		def set_all_LED_color(color):
			self.F_LED = color
			self.L_LED = color
			self.R_LED = color
			self.B_LED = color
			tell_arduino()


		def flash_LED(LED, color):
			#LED = color
			tell_arduino()
			sleep(0.2)


		def LED_color_cycle(color='G'):
			set_all_LED_color(0)
			
			for i in range(0,3):
				#front
				flash_LED(self.F_LED, color)
				#left
				self.F_LED = 0
				flash_LED(self.L_LED, color)
				#back
				self.L_LED = 0
				flash_LED(self.B_LED, color)
				#right
				self.B_LED = 0
				flash_LED(self.R_LED, color)

				set_all_LED_color(0)

		def control_connect_lightshow():
			def light_up():
				print 'lightshow start'
				for i in range(0,3):
					set_all_LED_color(0)
					eh.light.green.off()
					sleep(0.2)
					set_all_LED_color('G')
					eh.light.green.on()
					sleep(0.2)
				set_all_LED_color(0)
				eh.light.green.off()
				print 'lightshow end'
			v = threading.Thread(target=light_up)
			v.start()


		def collision_avoidance():
			self.coll = False
			if (self.state['FCLR'] != 'N'):
				self.coll = True
				if self.l_acc > 0 and self.r_acc > 0:
					(self.l_acc, self.r_acc) = (0,0)
					print 'front collision avoided!'

			elif (self.state['BCLR'] != 'N'):
				self.coll = True
				if self.l_acc < 0 and self.r_acc < 0:
					(self.l_acc, self.r_acc) = (0,0)
					print 'back collision avoided!'
					if self.state['BCLR'] == '1':
						self.B_LED = 'Y'
					elif self.state['BCLR'] == '2':
						self.B_LED = 'R'
			def obstacle_lights():
				self.obl = True
				while self.state['FCLR'] != 'N' or self.state['BCLR'] != 'N':
					#print 'obstacle lights start'
					if self.state['FCLR'] == '1':
						self.F_LED = 'Y'
					elif self.state['FCLR'] == '2':
						self.F_LED = 'R'
					if self.state['BCLR'] == '1':
						self.B_LED = 'Y'
					elif self.state['BCLR'] == '2':
						self.B_LED = 'R'
					tell_arduino()
				(self.F_LED, self.B_LED) = (0,0)
				tell_arduino()
				self.obl = False
				#print 'obstacle lights stop'
			
			if self.obl == False:
				w = threading.Thread(target=obstacle_lights)
				w.start()
				

		def tell_arduino():
			string = 'CMO:%s|LMO:%s|RMO:%s|DOOR:%s|F_LED:%s|L_LED:%s|R_LED:%s|B_LED:%s&' %(self.c_acc, self.l_acc, self.r_acc, self.door, self.F_LED, self.L_LED, self.R_LED, self.B_LED)
			#if string != self.command:
			self.command = string
			#print self.command
			#LEDS
			if self.F_LED != 0:
				arduino.write('6001\n')
				sleep(0.1)
			else:
				arduino.write('6002\n')
				sleep(0.1)
			if self.L_LED != 0:
				arduino.write('6003\n')
				sleep(0.1)
			else:
				arduino.write('6004\n')
				sleep(0.1)
			if self.R_LED != 0:
				arduino.write('6005\n')
				sleep(0.1)
			else:
				arduino.write('6006\n')
				sleep(0.1)
			if self.B_LED != 0:
				arduino.write('6007\n')
				sleep(0.1)
			else:
				arduino.write('6008\n')
				sleep(0.1)

			#MOTORS
			print 'LEFT: %s, RIGHT: %s, COMB: %s, DOOR: %s' %(self.l_acc, self.r_acc, self.c_acc, self.door)
			if self.l_acc == self.r_acc: #both drive motors moving at same speed
				output = int(1500+500*self.l_acc/100.0)
				if output == 2000:
					output = 1999
				arduino.write(str(output)+'\n')
				sleep(0.1)
			else: #drive motors moving at different speeds
				left = int(2500+500*self.l_acc/100.0)
				right = int(3500+500*self.r_acc*(-1)/100.0)
				if left == 3000:
					left = 2999
				if right == 4000:
					right = 3999
				arduino.write(str(left)+'\n')
				sleep(0.1)
				arduino.write(str(right)+'\n')
				sleep(0.1)
			comb = int(4500+500*self.c_acc/100.0) #comb
			if comb == 5000:
				comb = 4999
			arduino.write(str(comb)+'\n')
			if self.door == 'O': #door
				arduino.write('5999\n')
				sleep(0.1)
			elif self.door == 'C':
				arduino.write('5000\n')
				sleep(0.1)

				#arduino.write(string)
				


		def check_control():
			#toggle control on/off
			if self.keyval['START_btn']:
				#if (self.ctrl_swap - self.last_cmd) > 0.25:
					#self.last_cmd = self.new_cmd
					if self.control == 'M':
						self.control = 'A'
						print 'auto control'
						(self.l_acc, self.r_acc, self.c_acc) = (0,0,0)
						tell_arduino()
					else:
						self.control = 'M'
						print 'manual control'
						#control_connect_lightshow()
					


		def control():
		    define_allkeys()
		    self.keyval = {} #key values
		    for key in self.allkeys:
		    	self.keyval[key] = 0 #initialize all values to zero
		    set_defaults()
		    tell_arduino()
		    control_wait()
                    """
		    try:
				for event in self.gamepad.read_loop():
					for key in self.allkeys:
						[etype, ecode] = self.allkeys[key]
						if event.type == etype and event.code == ecode:
							self.keyval[key] = event.value
					pass_command()						
		    except:
				pass
      		    """
     		    while True:
     		         sleep(0.2)
     		         r,w,x = select([self.gamepad], [], [])
     		         for event in self.gamepad.read():
			     for key in self.allkeys:
			    	[etype, ecode] = self.allkeys[key]
				if event.type == etype and event.code == ecode:
		    		    self.keyval[key] = event.value
		    	     pass_command()
      		    
	   	############ this is where the program starts its loop
	    			

		t = threading.Thread(target=control)# need to work on this some more
		t.start()


		def talk_to_home():		
			print 'Awaiting network connection'
			onboard.waitalert1()
			self.data_loop = False
			network.wait(whenHearCall=heard)
			print 'Network connection made' 
			onboard.waitalert2()
			onboard.connalert1()
			while True:
				if network.isConnected()==False:
					onboard.connalert2()
					print 'Disconnected. Waiting for connection'
					cut = False
					while cut==False:
						#print 'attempt hang up'	
						try:
							network.hangUp()
							onboard.waitalert1()
							network.wait(whenHearCall=heard)
							cut = True
							#print 'hang up successful'
						except:
							pass
							#print 'cannot hang up'
					print "Connection made"
					onboard.waitalert2()
					onboard.connalert1()

		s = threading.Thread(target=talk_to_home)
		s.start()

app=App()

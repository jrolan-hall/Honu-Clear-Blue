from serial import Serial
import threading


ser = Serial('/dev/ttyACM0', 9600)

def ardinput():
	print 'listening to serial'
	while True:
		ln_in = ser.readline()
		if ln_in != '':
			print ln_in

x = threading.Thread(target=ardinput)
x.start()

while True:
	ln_out = raw_input('Command: ')
	ser.write(ln_out)
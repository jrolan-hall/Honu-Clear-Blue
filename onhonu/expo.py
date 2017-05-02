from serial import Serial
import threading
from time import sleep


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

	print 'forwards with combs on'
	for i in range(0,5):
		ser.write('1700\n')
		ser.write('2750\n')
		ser.write('4350\n')
	sleep(5)

	print 'stop'
	for i in range(0,5): #stop
		ser.write('6000\n')
	sleep(5)

	print 'reverse with combs off'
	for i in range(0,5): #reverse with combs off
		ser.write('1300\n')
	sleep(8)

	print 'door open'
	for i in range(0,5):
		ser.write('5999\n')
	sleep(5)

	print 'door close'
	for i in range(0,5):
		ser.write('5000\n')
	sleep(5)
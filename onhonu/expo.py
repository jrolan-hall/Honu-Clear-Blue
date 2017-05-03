from serial import Serial
import threading
from time import sleep
from subprocess import call
from random import random

ser = Serial('/dev/ttyACM0', 9600)

def ardinput():
	print 'listening to serial'
	while True:
		ln_in = ser.readline()

x = threading.Thread(target=ardinput)
x.start()

start_phrases = [15, 16, 17, 18, 35, 36, 37, 38, 39, 46, 47, 54, 55, 63, 75, 79, 110, 133]
stop_phrases = [32, 33, 34, 80]
dock_phrases = [10, 11, 52, 53, 60]

def pick_phrase(phrases):
	say = phrases[int(random()*len(phrases))]
	say = 'phrases/' + str(say) + '.wav'
	return say

call(["aplay", pick_phrase(start_phrases)])

while True:
	print 'forwards with combs on'
	call(["aplay", pick_phrase(start_phrases)])
	for i in range(0,10):
		ser.write('1700\n')
		ser.write('2750\n')
		ser.write('4350\n')
	sleep(5)

	print 'stop'
	for i in range(0,10): #stop
		ser.write('6000\n')
	call(["aplay", pick_phrase(stop_phrases)])
	sleep(5)

	print 'reverse with combs off'
	for i in range(0,10): #reverse with combs off
		ser.write('1300\n')
	sleep(8)

	print 'stop'
	for i in range(0,10):
		ser.write('6000\n')
	call(["aplay", pick_phrase(stop_phrases)])
	sleep(5)

	call(["aplay", pick_phrase(dock_phrases)])
	print 'door open'
	for i in range(0,10):
		ser.write('5999\n')
	sleep(12)

	print 'door close'
	for i in range(0,10):
		ser.write('5000\n')
	sleep(10)
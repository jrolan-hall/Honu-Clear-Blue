#!/usr/bin/env python

import pandas as pd
import numpy as np
#from staticmap import StaticMap, CircleMarker
from itertools import permutations as perm
from math import floor, cos, asin, sqrt, ceil
from heapq import nsmallest
import matplotlib.pyplot as plt
import pylab
from datetime import datetime, timedelta
from tzlocal import get_localzone
import pytz
import greedy
import os
import sys
import forecastio
from geopy.geocoders import Nominatim

def weather(latitude=40.807812, longitude=-73.962138): #alma mater coordinates
	key = '1ced27e7694f4424ebf7619967b53b4b'
	forecast = forecastio.load_forecast(key, latitude, longitude, units='si')
	byHour = forecast.hourly()
	byMinute = forecast.minutely()
	Hfuture = []
	Mfuture = []
	for hourlyData in byHour.data:
		time = hourlyData.time #timestamp
		temperature = hourlyData.temperature #celsius
		probability = hourlyData.precipProbability #chance of precipitation
		intensity = hourlyData.precipIntensity #amount of precipitation
		wind = hourlyData.windSpeed #wind speed 
		tick = [time, temperature, wind, probability, intensity]
		Hfuture.append(tick)
	for minutelyData in byMinute.data:
		time = minutelyData.time #timestamp
		#temperature = minutelyData.temperature #celsius
		probability = minutelyData.precipProbability #chance of precipitation
		intensity = minutelyData.precipIntensity #amount of precipitation
		#wind = minutelyData.windSpeed #wind speed mph
		tick = [time, probability, intensity]#, intensity]
		Mfuture.append(tick)
	Hfuture = np.array(Hfuture)
	Mfuture = np.array(Mfuture)
	times = Hfuture[:5,0]
	local_tz = get_localzone()
	hours = []
	for piutc in times:
		local_dt = piutc.replace(tzinfo=pytz.utc).astimezone(local_tz)
		local_dt = local_tz.normalize(local_dt)
		stamp = local_dt.strftime("%I %p")
		hours.append(stamp)
	geolocator = Nominatim()
	location = geolocator.reverse(str(latitude)+', '+str(longitude))
	return (Hfuture, Mfuture, hours, location.address)
		


def img_parse(struct, icons):
	images = {}
	infile = icons
	refs = np.array(infile)
	for ref in refs:
		for key in struct:
			if ref[0] == key and ref[1]==struct[key]:
				images[key]=ref[2]
	return images


def parse(string, icons):
	words = str(string)
	struct = eval(words)
	images = img_parse(struct, icons)
	struct = parse_time(struct)
	struct = parse_side_dists(struct)
	return (struct, images)


def tparse(string):
	words = str(string)
	struct = eval(words)
	struct = parse_time(struct)
	return struct


def parse_side_dists(struct):
	if str(struct['LCLR']) == 'N':
		struct['LDIST'] = u"\u221E"
	else:
		struct['LDIST'] = '0'
	if str(struct['RCLR']) == 'N':
		struct['RDIST'] = u"\u221E"
	else:
		struct['RDIST'] = '0'
	return struct


def parse_time(struct):
	local_tz = get_localzone()
	piutcdate = struct['DATE']
	piutctime = struct['TIME']
	piutcstamp = piutcdate + ' ' + piutctime
	piutc = datetime.strptime(piutcstamp, '%Y-%b-%d %I:%M:%S %p')
	local_dt = piutc.replace(tzinfo=pytz.utc).astimezone(local_tz)
	local_dt = local_tz.normalize(local_dt)
	struct['DATE'] = local_dt.strftime("%Y-%b-%d")
	struct['TIME'] = local_dt.strftime("%I:%M:%S %p")
	return struct


def formatcount(count):
	if count < 1001:
		return count
	elif (count > 1000) and (count <1000001):
		return str(round(count/1000.0,2)) + 'K'
	elif count > 1000000:
		return str(round(count/1000000.0,3)) +'M'


def formatcount2(count):
	if count < 1024:
		return str(count) + 'B'
	elif (count > 1024) and (count <1048576):
		return str(round(count/1024.0,0)) + 'kB'
	elif count > 1048576:
		return str(round(count/1048576.0,1)) +'MB'


def calcping(outtime, intime):
	trip1 = intime - outtime
	trip2 = outtime - intime
	if trip1 < trip2:
		trip = trip1
	else:
		trip = trip2
	ms = (trip.seconds*1000.0) + (trip.microseconds/1000.0)
	if ms > 999:
		return str(round(ms/1000.0,0)) + 's'
	else:
		return str(round(ms,0)) + 'ms'


def write_out(string, ip, incount):
	if incount%50==0:
		output = open('./logs/'+str(ip)+'-blackbox.txt', 'a')
		output.write('\n'+string)
		output.close()


def sort_devices(devices):
	while len(devices)<3:
		#devices.append(('localhost','000.00.000.000','testing'))#(alias, address, status)
		devices.append(('','',''))#
	avatars = []
	for device in devices:
		if device[2] == 'active':
			avatars.append('./images/ACTIVE.gif')
		elif device[2] == 'inactive':
			avatars.append('./images/INACTIVE.gif')
		else:
			avatars.append('./images/NULL.gif')
	return (devices, avatars)


def test_points():
	p0=('40.807912', '-73.962631')#3,4
	p1=('40.807714', '-73.962776')#5,11
	p2=('40.807603', '-73.961660')#12,8
	p3=('40.807315', '-73.961919')#9,5

	coor = [p0,p1,p2,p3]#, p4]
	lats = []
	lons = []
	for pt in coor:
		lats.append(pt[0])
		lons.append(pt[1])
	return (lats, lons)


def plot_area(lats, lons):
	points = complexify(lats, lons) #change to lons, lats
	points = change_ref(points)
	if len(points) > 2:
		(bound, area) = order_anchors(points)
	else:
		bound = points
		area = 0
	boundary = bound
	boundary.append(boundary[0])
	return (boundary, area)
	#plot_points(boundary, './images/AREA.png')


def plot_path(bound, pitch):
	#(N,E,W,S) = find_NEWS_bounds(bound)
	nodes = grid_overlay(bound[0],pitch,bound)#spacing = 0.000007 = 59.63cm at 40N
	#remove points outside of area
	nodes = remove_outer_points(bound, nodes)#PROBLEMS - kills everything
	#create distance matrix
	points = check_unique(bound, nodes)
	points = np.array(points)
	#print points
	(m,n) = np.meshgrid(points, points)	
	matrix = abs(m-n)
	sequence = greedy.solve_tsp(matrix)#PROBLEMS - won't stop
	path = order_points(sequence,points)
	length = calculateLength(path)
	return (path, matrix, length)


def route_plan(lats, lons, pitch): #anchor points
	#point 0 is always current location
	#sanity checks
	points = complexify(lats, lons)
	points = change_ref(points)
	if len(points)> 2:
		bound = order_anchors(points)
		#find furthest NEWS points%60
		(N,E,W,S) = find_NEWS_bounds(bound)
		#create overlay using those points
		nodes = grid_overlay(points[0],N,E,W,S,pitch, bound)#spacing = 0.000007 = 59.63cm at 40N
		#remove points outside of area
		nodes = remove_outer_points(bound, nodes)#PROBLEMS - kills everything
		#create distance matrix
		points = check_unique(bound, nodes)
		points = np.array(points)
		#print points
		(m,n) = np.meshgrid(points, points)
		matrix = abs(m-n)
		#print matrix
		#run christophides
		sequence = greedy.solve_tsp(matrix)#PROBLEMS - won't stop
		#print sequence
		path = order_points(sequence,points)
		plot_points(path, 'out.png')
	#plot points
	#plot arcs
	#render map
	#return points


def change_ref(points):
	#changes references to cartesian points to do route plan, uses complex notation
	lat_0 = points[0].real
	lon_0 = points[0].imag
	cart_pts = []
	for point in points:
		#find x_value - distance between lines of longitude
		x = round(cartesian(lat_0, lon_0, lat_0, point.imag),3) #lat held constant
		#find y_value - distance between lines of latitude
		y = round(cartesian(lat_0, lon_0, point.real, lon_0),3) #lon held constant
		pt = float(x) + float(y)*1j
		cart_pts.append(pt)
	return cart_pts


def cartesian(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295
    a = 0.5 - cos((lat2 - lat1) * p)/2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
    return 12742000 * asin(sqrt(a))


def complexify(lats, lons):
	output = []
	for i in range(0,len(lats)):
		pt = float(lats[i]) + float(lons[i])*1j
		output.append(pt)
	return output


def check_unique(bound, nodes):
	points = []
	for pt in bound:
		if pt not in points:
			points.append(pt)
	for nd in nodes:
		if nd not in points:
			points.append(nd)
	return points	


def order_anchors(points): #orders anchor points into config with largest area
	#duplicate point 0 and add to the end of the list
	#[p0,p1,p2,...pn,p0]
	points.append(points[0])
	#permutate points p1 to pn
	middle = points[1:-1]
	perms = list(perm(middle))
	(area, largest, sequence) = (0,0,0)
	for order in perms:
		#re-add point 0 to start and end
		ls = [points[0]]
		ls += order
		ls += [points[0]]
		#print ls
		boundary = []
		for pt in ls:
			boundary.append((pt.real,pt.imag))
		perm_area = shoelace_formula(boundary, absoluteValue=False)
		#print perm_area
		#print '\n'
		if perm_area > area:
			area = perm_area
			largest = perm_area
			sequence = ls
	sequence.pop(-1)
	return (sequence, largest)


def shoelace_formula(polygonBoundary, absoluteValue = True):
    nbCoordinates = len(polygonBoundary)
    nbSegment = nbCoordinates - 1

    l = [(polygonBoundary[i+1][0] - polygonBoundary[i][0]) * (polygonBoundary[i+1][1] + polygonBoundary[i][1]) for i in xrange(nbSegment)]

    if absoluteValue:
        return abs(sum(l) / 2.)
    else:
        return sum(l) / 2.

def calculateLength(path):
	total = 0
	for i in range(1, len(path)):
		curr = path[i]
		last = path[i-1]
		dist = calculateDistance(curr.real, curr.imag, last.real, last.imag)
		total += dist
	return total


def estimate_time(length, path):
	d = datetime(1,1,1)+timedelta(seconds=int(len(path)*0.5+(length/2.5))) #this is assuming 2.5m/s average speed and spends 0.5s at each node
	days = d.day-1
	hours = str(d.hour+days*24)
	mins = str(d.minute)
	secs = str(d.second)
	string = hours+' h, '+mins+' m, '+secs+'s'
	return string




def calculateDistance(x1,y1,x2,y2):  
     dist = sqrt((x2 - x1)**2 + (y2 - y1)**2)  
     return dist 


def find_NEWS_bounds(points):
	(N,E,W,S) = (0,0,0,0)
	(N_p, E_p, W_p, S_p) = (0,0,0,0)
	ref = points[0]
	for point in points: #lon= realparts, lat = imag parts
		N_dist = point.imag - ref.imag
		E_dist = point.real - ref.real
		W_dist = ref.real - point.real
		S_dist = ref.imag - point.imag
		if N_dist >= N:
			N_p = point
			N = N_dist
		if E_dist >= E:
			E_p = point
			E = E_dist
		if W_dist >= W:
			W_p = point
			W = W_dist
		if S_dist >= S:
			S_p = point
			S = S_dist
	#print N,E,W,S
	#print N_p,E_p,W_p,S_p
	return (N_p, E_p, W_p, S_p)


def grid_overlay(origin, spacing, points):
	corners = []
	for pt in points:
		corners.append(pt.real)
		corners.append(pt.imag)
	low = int(floor(min(corners)))
	hi = int(ceil(max(corners)))
	nodes = []
	for i in range(low, hi):
		for j in range(low, hi):
			node = i+j*1j
			nodes.append(node)
	return nodes


def remove_outer_points(bound, nodes):
	#unpack complexities
	poly = []
	for anchor in bound:
		point = (anchor.real, anchor.imag)
		poly.append(point)
	a_nodes = []
	for node in nodes:
		verdict = point_in_poly(node.real, node.imag, poly)
		if verdict == 'IN':
			a_nodes.append(node)
	return a_nodes


def point_in_poly(x,y,poly):
   # check if point is a vertex
   if (x,y) in poly: return "IN"
   # check if point is on a boundary
   for i in range(len(poly)):
      p1 = None
      p2 = None
      if i==0:
         p1 = poly[0]
         p2 = poly[1]
      else:
         p1 = poly[i-1]
         p2 = poly[i]
      if p1[1] == p2[1] and p1[1] == y and x > min(p1[0], p2[0]) and x < max(p1[0], p2[0]):
         return "IN"   
   n = len(poly)
   inside = False

   p1x,p1y = poly[0]
   for i in range(n+1):
      p2x,p2y = poly[i % n]
      if y > min(p1y,p2y):
         if y <= max(p1y,p2y):
            if x <= max(p1x,p2x):
               if p1y != p2y:
                  xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
               if p1x == p2x or x <= xints:
                  inside = not inside
      p1x,p1y = p2x,p2y
   if inside: return "IN"
   else: return "OUT"


def plot_points(path):#, name): #[(lat1,lon1),(lat2,lon2),...]
	#m = StaticMap(450,414)
	x = []
	y = []
	for point in path:
		(lon, lat) = (point.imag, point.real)
		x.append(lat)
		y.append(lon)
		#marker_outline = CircleMarker((lon,lat),'white',10)
		#marker = CircleMarker((lon,lat),'#0036FF',8)
		#m.add_marker(marker_outline)
		#m.add_marker(marker)
		#print 'plotted: ' + str(point)
	#return m
	#image = m.render()
	#image.save('MAP.png')
	fig = plt.figure(figsize=(4.5, 4.15))
	plt.scatter(x,y)
	plt.plot(x,y)
	#plt.savefig(name)
	plt.show()


def save_anchors(anchorslat, anchorslon, filename):
	save = open(filename, 'w')
	save.write('LATITUDE,LONGITUDE')
	for i in range(0, len(anchorslat)):
		save.write('\n'+anchorslat[i]+','+anchorslon[i])
	save.close()


def load_anchors(filename):
	load = pd.read_csv(filename)
	lats = []
	lons = []
	for lat in load['LATITUDE']:
		lats.append(str(lat))
	for lon in load['LONGITUDE']:
		lons.append(str(lon))
	return (lats, lons)


def order_points(sequence,points):
	path = []
	for i in range(0, len(sequence)):
		path.append(points[sequence[i]])
	#print path
	return path


def parse_blackboxes():
	boxes = os.listdir('./logs')
	log = open('./logs/compile.csv','w')
	log.write('ip,msg,size,date,time,ctrl,fdist,fclr,lclr,rclr,bclr,cmo,lmo,rmodoor,indi,bat,batl,vol,cmb,spd,tmp,hum,bear,alt,lat,lon,vnode,rnode')
	for box in boxes:
		ip = box.split('-')
		with open('./logs/'+box,'r') as bbox:
			for line in bbox:
				tick = line
				words = str(tick)
				S = eval(words)
				size = sys.getsizeof(tick)
				try:
					entry = '\n'+ip+','+S['MSG']+','+str(size)+','+S['DATE']+','+S['TIME']+','+S['CTRL']+','+S['FDIST']+','+S['FCLR']+','+S['LCLR']+','+S['RCLR']+','+S['BCLR']+','+S['CMO']+','+S['LMO']+','+S['RMO']+','+S['DOOR']+','+S['INDI']+','+S['BAT']+','+S['BATL']+','+S['VOL']+','+S['CMB']+','+S['SPD']+','+S['TMP']+','+S['HUM']+','+S['BEAR']+','+S['ALT']+','+S['LAT']+','+S['LON']+','+S['VNODE']+','+S['RNODE']	
					log.write(entry)	
				except:
					pass
			bbox.close()
	log.close()
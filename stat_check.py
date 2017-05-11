scripts = ['greedy.py', 'helper.py', 'honuhome.py', 'network.py', 'onboard.py', 'honuroam.py', 'popup.py', 'weaved.py']

results = []

for script in scripts:
	count = 0
	func = 0
	equals = 0
	objects = 0
	calls = 0
	chars = 0

	with open(script) as f:
		#print 'processing: '+ script
		for line in f:
			chars += len(line)
			if len(line) > 2:
				count += 1
			func += line.count('def')
			equals += line.count('=')-(2*line.count('=='))
			objects += line.count('self.')
			calls += line.count('(')
			
		result = {}

		result['name'] = script
		result['count'] = count
		result['func'] = func
		result['equals'] = equals
		result['object'] = objects
		result['calls'] = calls
		result['chars'] = chars

		results.append(result)

		#print script
		#print count, func, equals, objects, calls, chars

count = 0
func = 0
equals = 0
objects = 0
calls = 0
chars = 0

for result in results:
	count += result['count']
	func += result['func']
	equals += result['equals']
	objects += result['object']
	calls += result['calls']
	chars += result['chars']

print '\ncount|functions|equals|objects|calls|chars'
print  count, func, equals, objects, calls, chars
print 'average call rate (per second): '+str(calls*110)
print 'maximum call rate (per second): '+str(calls*500)
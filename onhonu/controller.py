import evdev

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
    return scale(value,(0,255),(-100,100))

def scale_trigger(value):
    return scale(value,(0,255),(0,100))

def control():
    print 'Finding PS3 Controller'
    gamepad = None
    while gamepad == None:
        devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
        for device in devices:
            if device.name == 'PLAYSTATION(R)3 Controller':
                ps3dev = device.fn
                gamepad = evdev.InputDevice(ps3dev)
                print 'Controller found'


    #format button name: [action, event type, event code, event value]
    array = {
        'cross button' : ['pressed', 1, 302, 1],
        'triangle button' : ['pressed', 1, 300, 1],
        'circle button' : ['pressed', 1, 301, 1],
        'square button' : ['pressed', 1, 303, 1],
        'left button' : ['pressed', 1, 295, 1],
        'right button' : ['pressed', 1, 293, 1],
        'up button' : ['pressed', 1, 292, 1],
        'down button' : ['pressed', 1, 294, 1],
        'select button' : ['pressed', 1, 288, 1],
        'start button' : ['pressed', 1, 291, 1],
        'L1 button' : ['pressed', 1, 298, 1],
        'L2 button' : ['pressed', 1, 296, 1],
        'R1 button' : ['pressed', 1, 299, 1],
        'R2 button' : ['pressed', 1, 297, 1],
        'L stick button' : ['pressed', 1, 289, 1],
        'R stick button' : ['pressed', 1, 290, 1],
        'left stick' : ['up/dn', 3, 1, 's'],
        'right stick' : ['up/dn', 3, 5, 's'],
        'left stick' : ['l/r', 3, 0, 's'],
        'right stick' : ['l/r', 3, 2, 's'],
        'L1 trigger' : ['held', 3, 50, 't'],
        'L2 trigger' : ['held', 3, 48, 't'],
        'R1 trigger' : ['held', 3, 51, 't'],
        'R2 trigger' : ['held', 3, 49, 't'],
        'LR accel' : ['tilted', 3, 59, 2], #change from 2 to 1 to activate
        'FB accel' : ['tilted', 3, 60, 2] #change from 2 to 1 to activate
        }

    for event in gamepad.read_loop():
        for key in array:
            [action, evtype, evcode, evval] = array[key]
            if event.type == 1 and event.code == evcode and event.value == evval:
                print key+' '+action
            elif event.type == 3 and event.code == evcode and evval == 's':
                speed = scale_stick(event.value)
                print key+' '+action+' '+str(speed)
            elif event.type == 3 and event.code == evcode and evval == 't':
                speed = scale_trigger(event.value)
                print key+' '+action+' '+str(speed)
            elif event.type == 3 and event.code == evcode and evval == 1:
                print key+' '+action+' '+str(event.value)


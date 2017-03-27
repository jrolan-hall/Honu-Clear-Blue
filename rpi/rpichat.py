from twilio.rest import TwilioRestClient
import socket
import fcntl
import struct

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def send_sms():
	account_sid = 'AC65fb6150306f45c06da3f6d1bba69888'
	auth_token  = 'dc723c6dc368e420eafc2c34a2d35ecc'
	client = TwilioRestClient(account_sid, auth_token)
	sms = 'Live! HMU @' + get_ip_address('wlan0')
	client.messages.create(
	    to='+16463206158', 
	    from_="13473345620", 
	    body=sms
	)

def main():
	#send_sms()
	import chat

main()
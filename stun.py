'''
Client for STUN (Session Traversal Utilities for NAT)
Author: Zhang NS (http://www.zhangns.tk/) <deltazhangns@163.com>
Latest revision: 30 Dec 2013
Written in Python 2.x
Based on UDP Protocol using Python Socket
Specification RFC5389 (http://tools.ietf.org/html/rfc5389) followed
Designed to obtain the corresponding reflexive transport address of a local transport address
Can be utilized in NAT Behavior Discovery and NAT Traversal, which are essential in advanced deployments of VoIP, SIP, and P2P
 
Warning:
This implementation is unreliable and unsafe.
Exception handling, retransmission mechanism, and response validation are imperfect.
Use at your own risk!
'''
 
import socket, platform, sys, random
 
if platform.python_version() >= '3.0.0':
##    sys.exit(input('Python 3 is not supported. Press enter to abort...'))
    ord = lambda x: x
    raw_input = input
 
print('STUN Client by Zhang NS <deltazhangns@163.com>')
print('Environment: Python %s on %s %s\n' % (platform.python_version(), platform.system(), platform.version()))
print('Defualt port for STUN: 3478')
servers = '''
numb.viagenie.ca
provserver.televolution.net
stun.callwithus.com
stun.counterpath.net
stun.ekiga.net
stun.ideasip.com
stun.internetcalls.com
stun.ipshka.com
stun.iptel.org
stun.l.google.com:19302
stun.noc.ams-ix.net
stun.phoneserve.com
stun.rixtelecom.se
stun.schlund.de
stun.sipgate.net
stun.sipgate.net:10000
stun.softjoys.com
stun.stunprotocol.org
stun.voip.aebc.com
stun.voiparound.com
stun.voipbuster.com
stun.voipstunt.com
stun.voxgratia.org
stun1.l.google.com:19302
stun1.voiceeclipse.net
stun2.l.google.com:19302
stun3.l.google.com:19302
stun4.l.google.com:19302
stun.ekiga.net
stunserver.org
stun.ideasip.com
stun.softjoys.com
stun.voipbuster.com
'''
print('''
Some currently available free STUN servers:
''' + servers)

server_list = []
for line in servers.splitlines():
    line = line.strip()
    if not line:
        continue
    if ':' in line:
        host, port = line.split(":", 1)
        port = int(port)
    else:
        host, port  = line, 3478
    if host:
        server_list.append((host, port))
 
BUFF = 4096
ID = b''
lenID = 96 // 8
timeout = 5
cookiemagic = b'\x21\x12\xa4\x42'
 
##HOST = raw_input('STUN server: ') or 'stun.schlund.de'
##PORT = int(raw_input('STUN server port number: ') or 3478)
##ADDR = HOST, PORT
 
def GenID(): # Generate 96 bits random string
    return bytes([random.randint(0, 0xFF) for i in range(lenID)])
    ret = b''
    for i in range(0, lenID):
        ret += chr(random.randint(0, 0xFF))
    return ret
 
def GenReq(): # Generate STUN Binding Request
    global ID
    ret = b''
    # STUN Message Type: 0x0001 Binding Request
    ret += b'\x00\x01'
    # Message Length is 0
    ret += b'\x00\x00'
    # Magic Cookie
    ret += cookiemagic
    # Transaction ID
    ID = GenID()
    ret += ID
    return ret
 
def GetTAddressByResponse(r): # Return tuple (IP, Port) or False
        # Is the Response a Success Response with Binding Method?
        # Check the first two bytes. Are they 0x0101, as promised?
        if r[0:2] != b'\x01\x01': return False
        # Are the last 2 bits of Message Length zero?
        if r[3] % 4 != 0: return False
        # Does the Response contain the correct Magic Cookie?
        if r[4:8] != cookiemagic: return False
        iter = 20 #iterator for traversal of r
        # Traverse the response to find the first MAPPED-ADDRESS attribute.
        while r[iter:iter + 2] != b'\x00\x01':
            iter = iter + 4 + 0x100 * ord(r[iter + 2]) + ord(r[iter + 3])
        port = 0x100 * ord(r[iter + 6]) + ord(r[iter + 7])
        IP = '%s.%s.%s.%s' % (ord(r[iter + 8]), ord(r[iter + 9]), ord(r[iter + 10]), ord(r[iter + 11])) #Dot-decimal notation
        return (IP, port)

 

c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
c.settimeout(timeout)
c.bind(('', 0))

while True:
    for server in server_list:
        try:
            c.sendto(GenReq(), server)
            print('STUN request sent...', server)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print('Error when sending request: %s' % e)
            continue
    try:
        print('-----------------------------')
        while 1:
            resp = c.recv(BUFF)
            taddr = GetTAddressByResponse(resp)
            if taddr:
                print('STUN server returns %s:%s' % taddr)
                print('\x07') # Indicate Success Response
            else:
                print('STUN server returns non-Success Response!')
    except Exception as e:
        import traceback
        traceback.print_exc()
        print('Error when receiving response: %s' % e)

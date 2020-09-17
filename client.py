import base64
import telnetlib
import time
import sys

with open(sys.argv[1], 'rb') as f:
    content = f.read()

name = base64.b64encode(sys.argv[2].encode('UTF-8'))
c = base64.b64encode(content)  # +b'\n'


tn = telnetlib.Telnet(sys.argv[3], port=sys.argv[4])
l = str(len(c)).encode('UTF-8')
tn.write(l+b'\n'+name+b'\n'+c+b'\n')

try:
    while (True):
        t = tn.read_eager()
        if (t):
            try:
                print(str(int(float(t) * 100)) + '%')
            except ValueError:
                print(t.decode('UTF-8'))
except (EOFError):
    print('connection closed')
tn.close()

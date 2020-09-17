import base64
import socket
from threading import Thread
import time
import os

clients = []


# Thread to listen one particular client
class ClientListener(Thread):
    def __init__(self, name: str, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock
        self.name = name

    def _close(self):
        clients.remove(self.sock)
        self.sock.close()
        print(self.name + ' disconnected')

    def run(self):
        data = b''
        count = 0
        read_meta = False
        name = None
        l = -1
        time_ = time.time()
        value = 0.0
        while True:
            rcv = self.sock.recv(4096)
            count += rcv.count(b'\n')
            data += rcv

            if (not read_meta and count >= 2):
                read_meta = True
                s = data.split(b'\n')
                l = int(s[0])
                name = s[1]
                if (len(s) == 3):
                    data = s[2]
                else:
                    data = b''

            if (read_meta and time.time() - time_ > 0.2):
                res = len(data) * 1.0 / l
                if (res-value > 0.05):
                    self.sock.send(str(res).encode('UTF-8'))
                    time_ = time.time()
                    value = res

            if (not rcv or count >= 3):
                break

        self.sock.send(b'1')

        content = base64.b64decode(data.replace(b'\n', b''))
        name = base64.b64decode(name).decode('UTF-8')

        files = [f for f in os.listdir(os.getcwd())
                 if os.path.isfile(os.path.join(os.getcwd(), f))]

        if (name in files):
            i = 0
            while ('(' + str(i) + ')' + name in files):
                i += 1
            name = '(' + str(i) + ')' + name

        self.sock.send(b'saved as ' + name.encode('UTF-8'))
        self._close()
        with open(name, 'wb') as f:
            f.write(content)


def main():
    next_name = 1

    # AF_INET – IPv4, SOCK_STREAM – TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # reuse address; in OS address will be reserved after app closed for a while
    # so if we close and imidiatly start server again – we'll get error
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # listen to all interfaces at 8800 port
    sock.bind(('', 8800))
    sock.listen()
    while True:
        # blocking call, waiting for new client to connect
        con, addr = sock.accept()
        clients.append(con)
        name = 'u' + str(next_name)
        next_name += 1
        print(str(addr) + ' connected as ' + name)
        # start new thread to deal with client
        ClientListener(name, con).start()


if __name__ == "__main__":
    main()

import argparse
import socket
from time import sleep
import time


class ServerConnectionError(Exception):
    pass

class ServerConnection():
    sock = None
    connected = False
    
    def __init__(self, host="fc00:1337::17/96", port="6667", nickname="LudBot", channel="global", ip_version="6", encoding="utf-8"):
        self.host = host
        self.port = int(port)
        self.nickname = nickname
        self.channel = channel
        self.encoding = encoding

        self.addr_fam = socket.AF_INET if ip_version == 4 else socket.AF_INET6
    
    def setup(self):
        if self.sock:
            print("[ServerConnection] Overriding previous socket setup.")
            self.sock.close()
        else:
            print("[ServerConnection] Initialising socket.")

        self.sock = socket.socket(self.addr_fam, socket.SOCK_STREAM)

        print("[ServerConnection] Socket initialised in", self.addr_fam, "at address", self.host, "and port", self.port, ".")

        print("[ServerConnection] Attempting to connect socket.")
        try:
            self.sock.connect((self.host, self.port))
        except:
            raise ServerConnectionError("Could not connect to server.")

        print("[ServerConnection] Connection established successfully.")
        self.connected = True

    def command_format(self, command, message):
        return command + " " + message + "\r\n"

    def send_command(self, command):
        if not self.sock:
            print("[ServerConnection] Socket not connected.")
            raise ServerConnectionError("Socket not connected.")
        
        self.sock.sendall(command.encode(self.encoding))

    def connect(self):
        self.nick(self.nickname)
        self.user(self.nickname, self.nickname)
        self.join(self.channel, "")

    def nick(self, nickname):
        cmd = self.command_format("NICK", nickname)
        self.send_command(cmd)

    def user(self, username, realname):
        cmd = self.command_format("USER", username + " 0 * :" + realname)
        self.send_command(cmd)

    def join(self, channel, key):
        cmd = self.command_format("JOIN", channel + " " + key)
        self.send_command(cmd)

    def listen(self):
        while self.connected:
            data = self.sock.recv(1024)

            if not data:
                self.connected = False
                return
            
            print(data)

# Parse command-line arguments
argparser = argparse.ArgumentParser(description='Runs an IRC chat bot.')

argparser.add_argument("--host", "-hs", default="fc00:1337::17/96", help="The hostname of the server to connect to.")
argparser.add_argument("--port", "-p", default="6667", help="The port to connect to on the host.")
argparser.add_argument("--name", "-n", default="LudBot", help="The nickname of the bot on the IRC server.")
argparser.add_argument("--channel", "-c", default="global", help="The channel for the bot to connect to.")

args = argparser.parse_args()


# Initialise ServerConnection
server = ServerConnection(args.host, args.port, args.name, args.channel)

server.setup()
server.connect()
server.listen()
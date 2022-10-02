import argparse
import socket
from time import sleep


class ServerConnectionError(Exception):
    pass

class ServerConnection():
    sock = None
    
    def __init__(self, host="fc00:1337::17/96", port="6667", nick="LudBot", channel="global", addr_fam="AF_INET6", encoding="utf-8"):
        self.host = host
        self.port = int(port)
        self.nick = nick
        self.channel = channel
        self.addr_fam = addr_fam
        self.encoding = encoding
    
    def setup(self):
        if sock:
            print("[ServerConnection] Overriding previous socket setup.")
            sock.close()
        else:
            print("[ServerConnection] Initialising socket.")

        sock = socket.socket(self.addr_fam, socket.SOCK_STREAM)
        sock.bind(self.host, self.port)

        print("[ServerConnection] Socket initialised in", self.addr_fam, "at address", self.host, "and port", self.port, ".")

    def sock_connect(self):
        print("[ServerConnection] Attempting to connect socket.")
        try:
            self.sock.connect()
        except:
            raise ServerConnectionError("Could not connect to server.")

        print("[ServerConnection] Connection established successfully.")

    def connect(self):
        self.sock_connect()

    def nick(self, nickname):
        cmd = self.command_format("NICK", nickname)
        self.send_command(cmd)

    def user(self, username, realname):
        cmd = self.command_format("USER", username + " 0 * :" + realname)
        self.send_command(cmd)

    def command_format(self, command, message):
        return command + " " + message + "\r\n"

    def send_command(self, command):
        if not sock:
            print("[ServerConnection] Socket not connected.")
            raise ServerConnectionError("Socket not connected.")
        
        sock.sendall(command.encode(self.encoding))




def prepare_message(message):
    
    bytes = message.encode("utf-8") + b'\r\n'
    return bytes


# Parse command-line arguments
argparser = argparse.ArgumentParser(description='Runs an IRC chat bot.')

argparser.add_argument("--host", "-hs", default="fc00:1337::17/96", help="The hostname of the server to connect to.")
argparser.add_argument("--port", "-p", default="6667", help="The port to connect to on the host.")
argparser.add_argument("--name", "-n", default="LudBot", help="The nickname of the bot on the IRC server.")
argparser.add_argument("--channel", "-c", default="global", help="The channel for the bot to connect to.")

args = argparser.parse_args()


# Initialise and connect socket
sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
try:
    print("Attempting connection to", args.host, "at port", args.port)
    sock.connect((args.host, int(args.port)))

except:
    print("Connection failed.")
    quit()

reg_string = ("NICK " + args.name).encode()
reg_string += ("USER " + args.name + " 0 * :" + args.name).encode()

sock.sendall(prepare_message("NICK " + args.name))
sock.sendall(prepare_message("USER " + args.name + " 0 * :" + args.name))

sleep(10)

sock.close()
import argparse
import socket
from time import sleep


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
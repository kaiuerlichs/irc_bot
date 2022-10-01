import argparse
import socket


# Parse command-line arguments
argparser = argparse.ArgumentParser(description='Runs an IRC chat bot.')

argparser.add_argument("--host", "-hs", default="fc00:1337::17/96", help="The hostname of the server to connect to.")
argparser.add_argument("--port", "-p", default="6667", help="The port to connect to on the host.")
argparser.add_argument("--name", "-n", default="LudBot", help="The nickname of the bot on the IRC server.")
argparser.add_argument("--channel", "-c", default="global", help="The channel for the bot to connect to.")

args = argparser.parse_args()



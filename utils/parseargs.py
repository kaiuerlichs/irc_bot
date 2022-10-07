""" Parses any command-line arguments amd returns all values or their default values """

import argparse

def parse(hostname, port, channel, nickname):
    # Parse command-line arguments
    argparser = argparse.ArgumentParser(description='Runs an IRC chat bot.')

    argparser.add_argument("--host", "-hs", default=hostname, help="The hostname of the server to connect to.")
    argparser.add_argument("--port", "-p", default=port, help="The port to connect to on the host.")
    argparser.add_argument("--name", "-n", default=nickname, help="The nickname of the bot on the IRC server.")
    argparser.add_argument("--channel", "-c", default=channel, help="The channel for the bot to connect to.")

    return argparser.parse_args()
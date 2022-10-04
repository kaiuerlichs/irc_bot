""" A simple IRC bot that can connect to an IRC server using TCP-IP.

The bot is able to establish a connection and respond to both channel and direct
messages, providing useful functionality for server users.
"""


from ast import main, match_case
import socket
import utils.config_loader as config_loader
import utils.parseargs as parseargs


class ServerConnectionError(Exception):
    """ Is raised when the ServerConnection has an exception. """
    pass


class Channel():
    def __init__(self, name):
        self.name = name
        self.users = []



class ServerConnection():
    """ Stores and maintains a connection to an IRC server.

    Attributes:
        host: The hostname of the IRC server, i.e. the IP address
        port: The port on the server that the IRC server is running on
        nickname: The nickname for the bot
        channel: The channel for the bot to join and listen on
        ip_version: The IP version to use
        encoding: The binary encoding to use

    Raises:
        ServerConnectionError: When the connection to the server behaves unexpectedly
    """
    sock = None
    connected = False
    
    def __init__(self, host="fc00:1337::17/96", port="6667", nickname="LudBot", channel="global", ip_version="6", encoding="utf-8"):
        """ Inits a ServerConnection """

        self.host = host
        self.port = int(port)
        self.nickname = nickname
        self.channel = channel
        self.encoding = encoding
        self.addr_fam = socket.AF_INET if ip_version == 4 else socket.AF_INET6
    
    def connect(self):
        """ Initialises the socket and connects it.

        Raises:
            ServerConnectionError: When the socket could not connect
        """

        # Close socket if already open
        if self.sock:
            print("[ServerConnection] Overriding previous socket setup.")
            self.sock.close()
        else:
            print("[ServerConnection] Initialising socket.")

        # Initialise socket with correct protocol and address family
        self.sock = socket.socket(self.addr_fam, socket.SOCK_STREAM)
        print("[ServerConnection] Socket initialised in", self.addr_fam, "at address", self.host, "and port", self.port, ".")

        # Open connection to server
        print("[ServerConnection] Attempting to connect socket.")
        try:
            self.sock.connect((self.host, self.port))
        except:
            raise ServerConnectionError("Could not connect to server.")

        # Set connected to true
        print("[ServerConnection] Connection established successfully.")
        self.connected = True

    def command_format(self, command, message):
        """ Format a command to send to the server.

        Args:
            command: The mesage command
            message: The params for the command
        """
        
        return command + " " + message + "\r\n"

    def send_command(self, command):
        """ Sends a formatted command to the server using the correct encoding.

        Args:
            command: A formatted command to send (see self.command.format)

        Raises:
            ServerConnectionError: When the socket is not connected
        """

        if not self.connected:
            raise ServerConnectionError("Socket not connected.")
        
        self.sock.sendall(command.encode(self.encoding))

    def logon(self):
        """ Handles the log-on sequence required to connect a client to the server. """

        self.nick(self.nickname)
        self.user(self.nickname, self.nickname)
        self.join(self.channel, "")

    # COMMAND RUNNERS
    def nick(self, nickname):
        cmd = self.command_format("NICK", nickname)
        self.send_command(cmd)

    def user(self, username, realname):
        cmd = self.command_format("USER", username + " 0 * :" + realname)
        self.send_command(cmd)

    def join(self, channel, key):
        cmd = self.command_format("JOIN", "#" + channel + " " + key)
        self.send_command(cmd)

    def pong(self, message):
        cmd = self.command_format("PONG", message)
        self.send_command(cmd)

    def handle_incoming(self, data):
        """ Takes incoming data and deconstructs it into commands and their parameters, then calls the correct command event handler

        Args:
            data: The data received from the server
        """

        # Decode data and split into separate command transmissions
        transmissions = data.decode(self.encoding).split("\r\n")

        for t in transmissions:
            if t == "":
                continue
            
            prefix = ""
            command = ""
            params = ""

            # Check if command is prefixed or not
            if t[0] == ":":
                deconstructed = t.split(' ', 2)
                prefix = deconstructed[0]
                command = deconstructed[1]
                if len(deconstructed) > 2:
                    params = deconstructed[2]
            else:
                deconstructed=t.split(' ', 1)
                command = deconstructed[0]
                if len(deconstructed) > 1:
                    params = deconstructed[1]

            # Call event handler
            match command:
                case "JOIN":
                    self.on_join(prefix, params)
                case "PING":
                    self.on_ping(params)
                case _:
                    print("Unknown command")

    # COMMAND EVENT HANDLERS   
    def on_join(self, prefix, params):
        pass

    def on_ping(self, params):
        self.pong(params)

    def listen(self):
        """ Monitors the data sent by the server.

        Raises:
            ServerConnectionError: If the server closes the connection unexpectedly
        """

        while self.connected:
            data = self.sock.recv(1024)

            if not data:
                self.connected = False
                raise ServerConnectionError("Connection closed by server.")
            
            self.handle_incoming(data)

if __name__ == "__main__":
    # Load config and parse command-line arguments
    conf = config_loader.load("./config.json")
    args = parseargs.parse(*conf)


    # Initialise ServerConnection
    server = ServerConnection(args.host, args.port, args.name, args.channel)
    server.connect()
    server.logon()
    server.listen()
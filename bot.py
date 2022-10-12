""" A simple IRC bot that can connect to an IRC server using TCP-IP.

The bot is able to establish a connection and respond to both channel and direct
messages, providing useful functionality for server users.
"""


import socket
import threading
import time
import utils.config_loader as config_loader
import utils.parseargs as parseargs
import utils.logger as logger
import utils.jokes as jokes


class ServerConnectionError(Exception):
    """ Is raised when the ServerConnection has an exception. """
    pass


class Channel():
    """ A simple class to hold information about the current channel

    Attributes:
        name: The name of the channel
        users: A set of all the users which are in the channel
        topic: The topic given to each channel
    """
    name = ""
    topic = ""
    users = []

    def __init__(self, name):
        self.name = name

    def addUser(self, user):
        if user not in self.users:
            self.users.append(user)

    def removeUser(self, user):
        if user in self.users:
            self.users.remove(user)

    def setTopic(self, topic):
        self.topic = topic


class ServerConnection:
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
    currentChannel = None
    
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
            logger.log("Overriding previous socket setup.")
            self.sock.close()
        else:
            logger.log("Initialising socket.")

        # Initialise socket with correct protocol and address family
        self.sock = socket.socket(self.addr_fam, socket.SOCK_STREAM)
        logger.log("Socket initialised in " + str(self.addr_fam) + " at address " + str(self.host) + " and port " + str(self.port) + ".")

        # Open connection to server
        logger.log("Attempting to connect socket.")
        try:
            self.sock.connect((self.host, self.port))
        except:
            raise ServerConnectionError("Could not connect to server.")

        # Set connected to true
        logger.log("Connection established successfully.")
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
                case "PRIVMSG":
                    self.on_privmsg(prefix, params)
                case "001":
                    self.on_rpl_welcome(params)
                case "002":
                    self.on_rpl_yourhost(params)
                case "003":
                    self.on_rpl_created(params)
                case "004":
                    self.on_rpl_myinfo(params)
                case "331":
                    self.on_rpl_notopic()
                case "332":
                    self.on_rpl_topic(params)
                case "353":
                    self.on_rpl_namreply(params)
                case _:
                    logger.log("Ignored " + command + " command from server, not implemented.")

    def send_channel_joke(self, channel):
        (setup, punch) = jokes.get()
        self.privmsg(channel, setup)
        time.sleep(1.0)
        self.privmsg(channel, punch)

    def get_nick_from_prefix(self, prefix):
        nick = prefix.split("!", 1)[0][1:]
        return nick

    # COMMAND RUNNERS (outgoing)
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

    def privmsg(self, target, message):
        cmd = self.command_format("PRIVMSG", target + " :" + message)
        self.send_command(cmd)

    def logon(self):
        """ Handles the log-on sequence required to connect a client to the server. """

        self.nick(self.nickname)
        self.user(self.nickname, self.nickname)
        self.join(self.channel, "")

    # COMMAND EVENT HANDLERS (incoming)
    def on_join(self, prefix, params):
        nick = self.get_nick_from_prefix(prefix) # Extract nickname from prefix
        
        if nick == self.nickname:
            self.currentChannel = Channel(params[1:])
            self.currentChannel.addUser(nick)

        else:
            self.currentChannel.addUser(nick)

    def on_ping(self, params):
        self.pong(params)

    def on_privmsg(self, prefix, params):
        nick = self.get_nick_from_prefix(prefix)

        tokens = params.split(":")
        target = tokens[0].strip()
        message = tokens[1]

        if target[0] == "#":
            if message[0] != "!":
                return

            match message.split(" ")[0][1:]:
                case "hello":
                    self.privmsg(target, "Hello " + nick)
                case "joke":
                    t = threading.Thread(target=self.send_channel_joke, args=(target, ))
                    t.start()
                case _:
                    self.privmsg(target, nick + ", I don't know this command.")

    def on_rpl_welcome(self, params): #001
        
        # :KaisLaptop.localdomain 001 LudBot :Hi, welcome to IRC
        msg = params.split(':')[1]
        logger.info(msg)

    def on_rpl_yourhost(self, params): #002
        # :KaisLaptop.localdomain 002 LudBot :Your host is KaisLaptop.localdomain, running version miniircd-2.1
        msg = params.split(':')[1]
        logger.info(msg)

    def on_rpl_created(self, params): #003
        # :KaisLaptop.localdomain 003 LudBot :This server was created sometime
        msg = params.split(':')[1]
        logger.info(msg)

    def on_rpl_myinfo(self, params): #004
        pass

    def on_rpl_luserclient(self): #251
        # :KaisLaptop.localdomain 251 LudBot :There are 1 users and 0 services on 1 server
        pass

    def on_err_nomotd(self): #422
        # :KaisLaptop.localdomain 422 LudBot :MOTD File is missing
        pass

    def on_rpl_motdstart(self): #375
        pass

    def on_rpl_motd(self): # 372
        pass

    def on_rpl_endofmotd(self): #376
        pass

    def on_rpl_notopic(self): #331
        self.currentChannel.setTopic("")

    def on_rpl_topic(self, params): #332
        # :KaisLaptop.localdomain 331 LudBot #global :<topic>
        topic = params.split(":")[1]
        self.currentChannel.setTopic(topic)

    def on_rpl_namreply(self, params): #353
        users = params.split(":")[1].split(" ")
        
        for user in users:
            self.currentChannel.addUser(user)

    def on_rpl_endofnames(self): #366
        # :KaisLaptop.localdomain 366 LudBot #global :End of NAMES list
        pass


if __name__ == "__main__":
    try:
        # Load config and parse command-line arguments
        conf = config_loader.load("./config.json")
        args = parseargs.parse(*conf)


        # Initialise ServerConnection
        server = ServerConnection(args.host, args.port, args.name, args.channel)
        server.connect()
        server.logon()
        server.listen()

    except KeyboardInterrupt:
        # Disconnect server here
        logger.log("Shutdown.")

    except ServerConnectionError:
        # Handle top-level connection errors here
        logger.log("Connection error.")
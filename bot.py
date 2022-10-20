""" A simple IRC bot that can connect to an IRC server using TCP-IP.

The bot is able to establish a connection and respond to both channel and direct
messages, providing useful functionality for server users.
"""

import random
import socket
import threading
import time
from datetime import datetime
import utils.config_loader as config_loader
import utils.parseargs as parseargs
import utils.logger as logger
import utils.jokes as jokes
import utils.facts as facts


class ServerConnectionError(Exception):
    """ Is raised when the ServerConnection has an exception. """
    pass


class Channel:
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


    def add_user(self, user):
        if user not in self.users:
            self.users.append(user)


    def remove_user(self, user):
        if user in self.users:
            self.users.remove(user)


    def set_topic(self, topic):
        self.topic = topic


    def log_users(self):
        logger.channel_info(self.name, self.topic, self.users)


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
    

    def __init__(self, host="fc00:1337::17", port="6667", nickname="LudBot", channel="global", ip_version="6", encoding="utf-8"):
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
                case "PART":
                    self.on_part(prefix)
                case "QUIT":
                    self.on_quit(prefix)
                case "001":
                    self.on_rpl_welcome(params)
                case "002":
                    self.on_rpl_yourhost(params)
                case "003":
                    self.on_rpl_created(params)
                case "004":
                    self.on_rpl_myinfo()
                case "251":
                    self.on_rpl_luserclient()
                case "331":
                    self.on_rpl_notopic()
                case "332":
                    self.on_rpl_topic(params)
                case "353":
                    self.on_rpl_namreply(params)
                case "366":
                    self.on_rpl_endofnames()
                case "422":
                    self.on_err_nomotd()
                case "372":
                    self.on_rpl_motd()
                case "375":
                    self.on_rpl_motdstart()
                case "376":
                    self.on_rpl_endofmotd()
                case "433":
                    self.on_err_nicknameinuse()
                case _:
                    logger.log("Ignored " + command + " command from server, not implemented.")


    def send_channel_joke(self, channel):
        """ Handle joke channel message """
        
        (setup, punch) = jokes.get()
        self.privmsg(channel, setup)
        time.sleep(1.0)
        self.privmsg(channel, punch)


    def send_private_fact(self, nick):
        """ Handle fact private message """

        fact = facts.get()
        self.privmsg(nick, fact)    


    def send_hello(self, channel, nick):
        """ Handle hello channel message """

        now = datetime.now()
        
        current_hour = int(now.strftime("%H"))
        greeting = ""

        # find correct greeting for present time
        if current_hour >= 17:
            greeting = "Bonsoir,"
        elif current_hour >= 12:
            greeting = "Bonne après-midi,"
        else:
            greeting = "Bon matin,"

        message = greeting + " " + nick + ". It is " + now.strftime("%A") + " and the time is " + now.strftime("%H:%M:%S.")
        
        self.privmsg(channel, message)
        

    def slap(self, sender, msg, channel):
        """ Handle slap channel message """

        try:
            user = msg.split(" ", 1)[1]

            # Slap user selected by sender
            if user.lower() in [x.lower() for x in self.currentChannel.users]:
                slap = "{} has slapped {} with a trout".format(sender, user)
                
            # Selected user not in the channel
            else:
                slap = "{} has tried to slap {} with a trout but sadly trouts can't hit imaginary friends".format(sender, user)
              
            self.privmsg(channel, slap)
            
        except:
            # Slap random user with trout
            tmpList = [x for x in self.currentChannel.users]
            if sender in tmpList:
           
                tmpList.remove(sender)
            
            user = random.choice(tmpList)
         
            slap = "{} has slapped {} with a trout".format(sender, user)
            self.privmsg(channel, slap)


    def get_nick_from_prefix(self, prefix):
        """ Extract nickname from a user prefix """

        nick = prefix.split("!", 1)[0][1:]
        return nick



    # -- COMMAND RUNNERS (outgoing) -- 

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


    def quit(self):
        cmd = self.command_format("QUIT", ":" + self.nickname + " is shutting down.")
        self.send_command(cmd)

    
    def logon(self):
        """ Handles the log-on sequence required to connect a client to the server. """

        self.nick(self.nickname)
        self.user(self.nickname, self.nickname)
        self.join(self.channel, "")


    def disconnect(self):
        """ Handle disconnect sequence to ensure protocol-correct exit and correct shutdown of socket """

        self.quit()
        self.sock.shutdown(socket.SHUT_RD)
        self.sock.close()



    # -- COMMAND EVENT HANDLERS (incoming) --

    def on_join(self, prefix, params):
        """ Handle JOIN commands, log successful join or other incoming users"""

        nick = self.get_nick_from_prefix(prefix)
        
        # If self is joining
        if nick == self.nickname:
            self.currentChannel = Channel(params[1:])
            self.currentChannel.add_user(nick)

        # If new user is joining
        else:
            self.currentChannel.add_user(nick)
            self.currentChannel.log_users()


    def on_ping(self, params):
        """ Respond to ping message """
        self.pong(params)
    
    
    def on_part(self, prefix):
        nick = self.get_nick_from_prefix(prefix)
        self.currentChannel.remove_user(nick)
        self.currentChannel.log_users()


    def on_privmsg(self, prefix, params):
        """ Parses incoming messages and dispatches the correct event handler depending on context and command """

        nick = self.get_nick_from_prefix(prefix)

        tokens = params.split(":")
        target = tokens[0].strip()
        message = tokens[1]

        # Remove channel membership prefixes (irrelevant to bot functionality)
        target.replace("+", "")
        target.replace("~", "")
        target.replace("&", "")
        target.replace("@", "")
        target.replace("%", "")
        
        # Message context is channel message
        if target[0] == "#":
            # Message is not a command, ignore
            if message[0] != "!":
                return

            # Match command to list of valid commands
            # Dispatch web-based event handlers on separate threads to ensure performance
            match message.split(" ")[0][1:]:
                case "hello":
                    self.send_hello(target, nick)
                case "joke":
                    try:
                        t = threading.Thread(target=self.send_channel_joke, args=(target, ))
                        t.start()
                    except jokes.APIException:
                        self.privmsg(target, nick + ", I'm struggling to think of any jokes right now.")
                case "slap":
                    self.slap(nick, message, target)
                case _:
                    self.privmsg(target, nick + ", I don't know this command.")

        # Message context is private message
        # Dispatch web-based event handlers on separate threads to ensure performance
        else:
            try:
                t = threading.Thread(target=self.send_private_fact, args=(nick, ))
                t.start()
            except facts.APIException:
                self.privmsg(target, nick + ", I can't think of any interesting facts right now.")


    def on_rpl_welcome(self, params): #001
        """ Logs welcome message from server to console"""

        msg = params.split(':')[1]
        logger.info(msg)


    def on_rpl_yourhost(self, params): #002
        """ Logs host info from server to console """

        msg = params.split(':')[1]
        logger.info(msg)


    def on_rpl_created(self, params): #003
        """ Logs server creation time to console """

        msg = params.split(':')[1]
        logger.info(msg)


    def on_rpl_myinfo(self): #004
        pass
    

    def on_rpl_luserclient(self): #251
        pass
    

    def on_err_nomotd(self): #422
        pass


    def on_rpl_motdstart(self): #375
        pass


    def on_rpl_motd(self): # 372
        pass


    def on_rpl_endofmotd(self): #376
        pass


    def on_rpl_notopic(self): #331
        self.currentChannel.set_topic("")


    def on_rpl_topic(self, params): #332
        """ Parses and sets the channel topic """

        topic = params.split(":")[1]
        self.currentChannel.set_topic(topic)


    def on_rpl_namreply(self, params): #353
        """ Parses user list transmitted upon joining channel """

        users = params.split(":")[1].split(" ")
        
        for user in users:
            self.currentChannel.add_user(user)


    def on_rpl_endofnames(self): #366
        self.currentChannel.log_users()


    def on_quit(self, prefix):
        """ Removes leaving user from channel user list and logs the result """

        nick = self.get_nick_from_prefix(prefix)
        self.currentChannel.remove_user(nick)
        self.currentChannel.log_users()


    def on_err_nicknameinuse(self): #433
        """ Adjust nickname if default is already in use """

        if self.nickname == "LudBot":
            self.nickname = "LudBot1"
            self.logon()

        else:
            num = int(self.nickname[6:])
            if num > 99:
                logger.log("All nicknames in use. Shutting down.")
                self.disconnect()
                quit()
            
            self.nickname = "LudBot" + str(num+1)
            self.logon()


if __name__ == "__main__":
    connected = False
    connection_count = 0

    # Attempt connection three times
    while connection_count < 3:
        try:
            # Load config and parse command-line arguments
            conf = config_loader.load("./config.json")
            args = parseargs.parse(*conf)

            # Initialise ServerConnection
            server = ServerConnection(args.host, args.port, args.name, args.channel)
            server.connect()

            connected = True

            server.logon()
            server.listen()

        except KeyboardInterrupt:
            # Handle CTRL-C to shut down bot
            server.disconnect()
            logger.log("Bot has shut down.")
            quit()

        except ServerConnectionError:
            if connected:
                connected = False
                connection_count = 0

            if connection_count < 2:
                # Handle top-level connection errors here
                connection_count += 1
                logger.log("Could not establish connection to server. Attempting again in 5 seconds... \n")
                time.sleep(5)

            else:
                # Handle top-level connection errors here
                connection_count += 1
                logger.log("Could not establish connection to server after 3 attempts. Bot shut down.")

        except:
            logger.log("An unexpected error has caused the bot to shut down.")
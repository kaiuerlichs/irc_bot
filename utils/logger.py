""" Provides functions to print formatted log messages to the console """

COLOUR_CYAN = "\u001b[36m"
COLOUR_YELLOW = "\u001b[33m"
COLOUR_MAGENTA = "\u001b[35m"
COLOUR_RESET = "\u001b[0m"


def info(message):
    print(COLOUR_CYAN + "[INFO] " + COLOUR_RESET + message)

def log(message):
    print(COLOUR_YELLOW + "[LOG] " + COLOUR_RESET + message)

def channel_info(channel, topic, users):
    print(COLOUR_MAGENTA + "[CHANNEL INFO] " + COLOUR_RESET + "Current Channel: " + channel)
    print(COLOUR_MAGENTA + "[CHANNEL INFO] " + COLOUR_RESET + "Topic: " + topic)
    print(COLOUR_MAGENTA + "[CHANNEL INFO] " + COLOUR_RESET + "Users: " + ", ".join(users))
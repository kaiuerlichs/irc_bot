""" Provides functions to print formatted log messages to the console """

COLOUR_CYAN = "\u001b[36m"
COLOUR_YELLOW = "\u001b[33m"
COLOUR_RESET = "\u001b[0m"


def info(self, message):
    print(COLOUR_CYAN + "[INFO] " + COLOUR_RESET + message)

def log(self, message):
    print(COLOUR_CYAN + "[LOG] " + COLOUR_RESET + message)
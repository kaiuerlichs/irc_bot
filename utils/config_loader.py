""" Loads a config file and returns the default values for the IRC connection params """

import json

def load(conf: str):
    with open(conf, "r") as f:
        config = json.load(f)

        return config["hostname"], config["port"], config["channel"], config["nickname"]
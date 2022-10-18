""" Pulls jokes from a web API """

import requests


class APIException(Exception):
    pass


API_URL = "https://official-joke-api.appspot.com/jokes/programming/random"


def get():
    try:
        res = requests.get(API_URL, timeout=10)
        res.raise_for_status()
    except:
        raise APIException("Could not retrieve joke")

    data = res.json()

    return (data[0]["setup"], data[0]["punchline"])
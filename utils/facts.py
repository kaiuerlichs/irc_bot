import requests

LIMIT = 1
API_URL = 'https://api.api-ninjas.com/v1/facts?limit={}'.format(LIMIT)
API_KEY = 'JU1mqc0Wij2j7usFwu/qpA==qk2jH3KI1ct9bnpg'

class APIException(Exception):
    pass 

def get():
    try:
        res = requests.get(API_URL, headers={'X-Api-Key': API_KEY})
        res.raise_for_status()
    except:
        raise APIException("Could not retrieve joke")

    data = res.json()

    return data[0]["fact"]
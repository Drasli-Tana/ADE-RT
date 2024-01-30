import json

import utils

with open("resources/config.json") as file:
    data = json.load(file)    
cal = utils.get_events(data)
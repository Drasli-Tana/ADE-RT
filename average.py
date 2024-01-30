import datetime as DT
import json

import utils
import projet10 as PJ

with open("resources/config.json") as file:
    data = json.load(file)    
cal = utils.get_events(data, "31885", "2023-09-01", "2024-09-01")

dates = set()
total_time = DT.timedelta()

for event_unparsed in PJ.extract_events(cal):
    event = utils.parse_event(event_unparsed, toCsv=False, code=False)
    dates.update((event["DTSTART"].date(), ))
    
    total_time += event["DUREE"]

total = (total_time / len(dates) * 5)
total2 = (total.days * 86400 + total.seconds) / 3600
print(total2)
#print(len(dates))
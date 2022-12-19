import datetime as DT
import random as RD

import requests
import PIL.Image as PI
import PIL.ImageDraw as PID

import projet10 as PJ

URL_ADE = (
    "https://ade-uga-ro-vs.grenet.fr/jsp/custom/modules/plannings/" +
    "anonymous_cal.jsp")
PROJECT_ID = "5"
lundi_8h = DT.datetime(2022, 12, 5, 8)
# I don't know if this will change or not, so let's put this in a constant
def getEvents(dateStart, dateEnd, download=True):
    if download or changed():
        cal = requests.get(
            URL_ADE, params={
                "resources": "49473",       # Groupe
                "projectId": PROJECT_ID,    # ??
                "calType": "ical",          # Type: ICalendar
                "firstDate": "2022-12-05",  # Lundi
                "lastDate": "2022-12-10"})  # Samedi

        with open("calendrier.ics", mode="w") as file:
            file.write(cal.content.decode("utf-8").replace("\n", ""))
        # /!\ lines ends with \r\n - Take this in account when modifying (currently
        # stripping it)
        # This works, don't touch! Prevents carriage return in description.

        return cal.content.decode("utf-8").replace("\n ", "").replace("\r", "")

    else:
         with open("calendrier.ics", mode="r") as file:
            return file.read()

def changed():
    return False

def parse_event(event: str, **kwargs):
    return PJ.parse_event(event, toCsv=False, code=False)

events = [parse_event(event, toCsv=False, code=False)
          for event in PJ.extract_events(getEvents(None, None, False))]

base = PI.new("RGB", (800, 600))
rectangles = PID.Draw(base)


for event in events:
    ecart = event.get("DTSTART") - lundi_8h

    rectangles.rectangle(
        [(ecart.days * 160, ecart.seconds / 60), 
        ((ecart.days + 1) * 160, (ecart.seconds + event["DUREE"].seconds) / 60)])

    rectangles.text(
        (ecart.days * 160, ecart.seconds / 60), event["SUMMARY"])
"""
rectangles.rectangle([(0, 0), (160, 60)])
rectangles.rectangle([(0, 60), (160, 120)])
rectangles.text((0, 0), "test")"""
base.show()

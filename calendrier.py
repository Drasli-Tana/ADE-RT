import datetime as DT
import random as RD

import requests
import PIL.Image as PI
import PIL.ImageDraw as PID
<<<<<<< HEAD
from PIL import ImageFont
=======
>>>>>>> b76aca8ac74d857be4cd8bb0b9775b923fdfeab1

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

<<<<<<< HEAD
base = PI.new("RGB", (961, 600))
rectangles = PID.Draw(base)
font = ImageFont.truetype("arial.ttf", 12)
=======
base = PI.new("RGB", (800, 600))
rectangles = PID.Draw(base)

>>>>>>> b76aca8ac74d857be4cd8bb0b9775b923fdfeab1

for event in events:
    ecart = event.get("DTSTART") - lundi_8h

    rectangles.rectangle(
<<<<<<< HEAD
        [((ecart.days + 1) * 160, ecart.seconds / 60), 
        ((ecart.days + 2) * 160, (ecart.seconds + event["DUREE"].seconds) / 60)])

    rectangles.text(
        (
            (ecart.days + 1.5) * 160,
            (ecart.seconds + event["DUREE"].seconds / 2) / 60),
        event["SUMMARY"],
        anchor="mm", align="center", font=font)
=======
        [(ecart.days * 160, ecart.seconds / 60), 
        ((ecart.days + 1) * 160, (ecart.seconds + event["DUREE"].seconds) / 60)])

    rectangles.text(
        (ecart.days * 160, ecart.seconds / 60), event["SUMMARY"])
>>>>>>> b76aca8ac74d857be4cd8bb0b9775b923fdfeab1
"""
rectangles.rectangle([(0, 0), (160, 60)])
rectangles.rectangle([(0, 60), (160, 120)])
rectangles.text((0, 0), "test")"""
base.show()
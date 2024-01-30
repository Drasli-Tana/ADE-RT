import datetime as DT
import random as RD
import locale as LC
import hashlib
import json
import os

import discord as DS
import discord.ext.commands as DC

import requests
import PIL.Image as PI
import PIL.ImageDraw as PID
import PIL.ImageFont as PIF

import projet10 as PJ
import utils

class ADEBot(DC.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with open("resources/config.json", mode='r') as file:
            self.config = json.load(file)

        self.font = PIF.truetype("arial.ttf", 11)

    async def on_ready(self):
        await self.tree.sync()

    def get_events(self, resource, dateStart, dateEnd, download=False):
        utils.get_events(self.config, resource, dateStart, dateEnd, download)

    def parse_event(self, event: str, **kwargs):
        """
        This is a doc-string
        """
        return PJ.parse_event(event, toCsv=False, code=False)

    def generate_grids(self, filename, inverted=False):
        """
        Generates a new base grid, with hours only.
        
        Colors depends of whether the inverted parameter is enabled or not
        Inverted means grey lines, white background and black letters.
        Non-inverted means grey lines, black background and white letters.
        
        Generated image is 881px wide, 671px tall.

        Saves as base.png when non inverted and base_inverted.png otherwise.

        Don't look at this.
        """
        base = PI.new("RGB", (881, 671),
            color=(255, 255, 255) if inverted else (0, 0, 0))
        rectangles = PID.Draw(base)
        start = DT.datetime(hours=8)

        for i in range(1, 7):
                rectangles.line(((i - .5) * 160, 0, (i - .5) * 160, 660),
                    fill=(127, 127, 127))

        ecart = DT.timedelta()
        variation = DT.timedelta(minutes=30)

        for i in range(1, 12):
            heure_date = (start + ecart)
            rectangles.text(
                (10, (i) * 60),
                heure_date.strftime("%Hh%M"),
                anchor="lm", align="center", font=self.font,
                fill=(0, 0, 0) if inverted else (255, 255, 255))

            rectangles.line((50, i * 60, 961, i * 60), fill=(127, 127, 127))
           
            ecart += variation
            heure_date = (start + ecart)
            
            rectangles.text(
                (10, (i + .5) * 60),
                heure_date.strftime("%Hh%M"),
                anchor="lm", align="center", font=self.font,
                fill=(0, 0, 0) if inverted else (255, 255, 255))
            
            rectangles.line((50, (i + .5) * 60, 961, (i + .5) * 60),
                fill=(192, 192, 192) if inverted else (63, 63, 63))

            ecart += variation

        base.save(filename)
        return base

    def open_grid(self, inverted=False):
        """
        Loads a base grid, inverted or not, and triggers the generation of
        it if it doesn't exists.
        """
        filename = f"resources/grid{'_inverted' if inverted else ''}.png"
        
        return (PI.open(filename)
                if os.path.exists(filename)
                else generate_grids(filename, inverted))

    def get_image(self, events, resource, start):
        """
        Returns a planning for the specified resource.

        Resource means here the unique identifier on the server associated
        with the group, and this ID is used to save an image, allowing it
        to be reused later (cache)
        """
        if events is None:
            # No change nor force download, using cached image
            base = PI.open(f"cache/{resource}.png")

        else:
            base = self.open_grid(inverted)
            rectangles = PID.Draw(base)

            ecart = DT.timedelta()
            variation = DT.timedelta(days=1)
            for i in range(1, 7):
                heure_date = (start + ecart).strftime("%A %d/%m/%Y").capitalize()
                rectangles.text(
                    (
                        (i) * 160, 30),
                    heure_date,
                    anchor="mm", align="center", font=self.font, 
                    fill=(0, 0, 0) if inverted else (255, 255, 255))
                ecart += variation    

            for event_unparsed in PJ.extract_events(events):
                event = parse_event(event_unparsed, toCsv=False, code=False)

                ecart = event.get("DTSTART") - start

                rectangles.rectangle(
                    [((ecart.days + .5) * 160, (ecart.seconds + 3600) / 60), 
                    (
                        (ecart.days + 1.5) * 160,
                        (ecart.seconds + event["DUREE"].seconds + 3600) / 60)],
                    fill=(255, 255, 255) if inverted else (0, 0, 0),
                    outline=(0, 0, 0) if inverted else (255, 255, 255))

                rectangles.text(
                    (
                        (ecart.days + 1) * 160,
                        (ecart.seconds + event["DUREE"].seconds / 2 + 3600) / 60),
                    "\n".join([event["SUMMARY"], event["LOCATION"].replace("\\|", "\n")]),
                    anchor="mm", align="center", font=self.font,
                    fill=(0, 0, 0) if inverted else (255, 255, 255))

            base.save(f"cache/{resource}.png")

        return events is None


LC.setlocale(LC.LC_TIME, "")

inverted = False 

intents = DS.Intents.default()
intents.message_content = True
bot = ADEBot(command_prefix='!', intents=intents)

@bot.tree.command(
        name="ade",
        description="Obtenir une capture d'écran de la semaine actuelle sur ADE.")
async def ade(interaction: DS.Interaction):
    if str(interaction.channel_id) not in bot.config["channels"]:
        await interaction.response.send_message(content="Channel invalide !")
        return
    
    # retard SNCF
    await interaction.response.defer()
    
    resource = bot.config["channels"][str(interaction.channel_id)]["ade_resource"]
    group = bot.config["channels"][str(interaction.channel_id)]["group"]

    today = DT.datetime.today()
    start = today - DT.timedelta(days=today.weekday())
    end = start + DT.timedelta(days=4)
    events = bot.get_events(
        resource, start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
    cache = bot.get_image(events, resource, start)

    file = DS.File(f"cache/{resource}.png", filename="ade.png")

    embed = DS.Embed()
    embed.title = (
        f"Emploi du temps ADE du {start.strftime('%d/%m/%Y')} au "
        f"{end.strftime('%d/%m/%Y')} - Groupe {group}")
    embed.color = 0xFF5733
    embed.description = (
        "Pour accéder directement à ADE, [cliquez ici]("
        f"{bot.config['base_url']}). Si l'emploi du temps est vide veuillez "
        "relancer la commande (merci ADE)." +
        ("\nImage envoyée depuis le cache." if cache else ""))
    embed.set_image(url=f"attachment://ade.png")
    embed.set_footer(text="BUT RT 2022/2023")

    await interaction.followup.send(file=file, embed=embed)

with open("resources/token.json") as file:
    bot.run(json.load(file)["token"])


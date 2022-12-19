# coding: UTF-8
"""
Script: SAE15/projet10
Création: hawkwant, le 09/11/2021
"""
# Imports
import time
import datetime

# Fonctions 
def convert_UTC_2_local(date: datetime.datetime):
    if time.localtime().tm_isdst:
        timedelta = datetime.timedelta(seconds=-time.altzone)

    else: 
        timedelta = datetime.timedelta(seconds=-time.timezone)

    return date + timedelta

def extract_events(ics: str):
    """
    This function extracts all events from an ics-like sting, and
    returns them as a list
    """
    events = ics.split("BEGIN:VEVENT\n")[1:]
    # We remove the header starting with "BEGIN:VCALENDAR"
    # Then, we remove the end of the original ics, we have now each event
    # one per index of the 'events' list
    return [event.split("END:VEVENT\n")[0] for event in events]

def parse_event(event: str, toCsv=True, code=True):
    dictionnary = dict()
    # Since each event is described by an identifier and a value, we use a
    # dictionnary with the same structure to modify and format this one.

    event = event.split("\n")[: -1]
    # The last element of this list is an empty string, this could cause an
    # issue with the dictionnary so we get rid of it

    for line in event:
        line = line.split(':')
        dictionnary[line[0]] = line[1]

    # Casts a string to a dictionnary, to be able to use each keys directly
    # without having to search in the list all the time
    dictionnary["DESCRIPTION"] = dictionnary.get(
        "DESCRIPTION", '').replace(',', '|')

    dictionnary["LOCATION"] = dictionnary.get("LOCATION", '').replace(',', '|')
    dictionnary["CATEGORIES"] = dictionnary.get(
        "CATEGORIES", '').replace(',', '|')

    dictionnary["DTSTART"] = convert_UTC_2_local(datetime.datetime.strptime(dictionnary["DTSTART"], "%Y%m%dT%H%M%SZ"))
    dictionnary["DTEND"] = convert_UTC_2_local(datetime.datetime.strptime(dictionnary["DTEND"], "%Y%m%dT%H%M%SZ"))
    dictionnary["DUREE"] = dictionnary["DTEND"] - dictionnary["DTSTART"]
    # We take the start and the end hour, with a HHMM format, to calculate the
    # duration of the class.
    if (code): 
        module = dictionnary["SUMMARY"].split('-')
        if len(module) < 3:
            dictionnary["CODE"] = "Autre"
            dictionnary["MODALITE"] = ''

        else:
            dictionnary["CODE"] = module[0]
            dictionnary["MODALITE"] = module[1]

    if toCsv:
        formatter = [
            "UID", "DATE", "HEURE", "DUREE", "CODE", "MODALITE", "SUMMARY",
            "LOCATION", "DESCRIPTION", "CATEGORIES"]
        return ';'.join([dictionnary.get(clef) for clef in formatter])

    else:
        return dictionnary

def export_markdown(resultats: list):
    titre = "| Module | Début | Fin | DS |\n"
    titre += "| :----- | :---- | :-- | :-- |\n"
    for ligne in resultats:
        titre += '|' + ligne.replace(';', '|') + '|\n'

    with open("README.md", mode='w') as file:
        file.write(titre)

def dates_module(events: list, group: str, module: str):
    eventsModule = [event for event in events
                    if group in event and module.split('-')[0] in event]
    # Limits the event list to all events from a module that concerns the
    # specified group
    duration = [event.split(";")[1] for event in eventsModule
                if "DS" not in event]
    # Takes the two first events that are not a test to make a span.
    # This list is no longer used after these two lines
    ds = None
    date1 = duration[0]  # Takes the date of the first event
    try:
        date2 = duration[1]  # Takes the date of the second event, if exists

    except IndexError:
        date2 = date1
        # Prevents an error when there is only one date

    else:
        if compare_dates(date1, date2) > 0:
            date1, date2 = date2, date1
    # Testing if two dates are well sorted is pointless if they are the same

    # Now, we will see for each event that is not a test if it is in the
    # interval, and if not, it will become the new limit from a side
    for event in eventsModule:
        date = event.split(';')[1]
        if "DS" not in event:
            if not date_dans_intervalle(date, date1, date2):
                if compare_dates(date, date1) < 0:
                    date1 = date

                else:
                    date2 = date
        else:
            ds = date
    return [date1, date2, ds]

def traitement(events: list, group: str):
    dates = dict()
    for module in TC.RESSOURCES_S1 + TC.SAES_S1:
        dates[module] = dates_module(events, group, module)
    # Computes the dates of each module, currently works only for the first
    # semester
    modulesDate = []
    for module in dates:
        date = f"{module};{dates[module][0]};{dates[module][1]};"
        if dates[module][2] is None:
            date += "-"

        else:
            date += dates[module][2]

        modulesDate.append(date)
    # Constructs a list of modules and dates,
    return modulesDate

def calcul_heure_fin(heure_debut: str, duree: str):
    heure_debut = heure_debut.split(':')
    duree = duree.split(':')

    heure_fin = [int(heure_debut[i]) + int(duree[i]) for i in range(2)]
    # Creation of a list that contains the end timestamp. At this point, this
    # can be over 24 for the hour and 60 for the minutes

    heure_offset = heure_fin[1] // 60
    # If minutes are over 60, we must add the correct amount of hours, probably
    # between 0 and 1
    heure_fin[1] %= 60
    # Now we have a valid amount of minutes

    heure_fin[0] = (heure_fin[0] + heure_offset) % 24
    # The "% 24" is used to prevent having 25:XX, which is equivalent to 1:XX

    return f"{heure_fin[0]:02d}:{heure_fin[1]:02d}"

def date_dans_intervalle(date: str, debut: str, fin: str):
    return (compare_dates(date, debut) >= 0) and (compare_dates(date, fin) <= 0)

def compare_dates(date1: str, date2: str):
    date1 = [int(i) for i in date1.split('-')]
    date2 = [int(i) for i in date2.split('-')]
    # Converts a date in a list of values

    difference = [date1[i] - date2[i] for i in range(3)]
    # A list of time differences, with at the first index the day, and at the
    # last one the year.
    difference[1] *= 32
    difference[2] *= 32 * 13
    # Then, we add a weight to our date, the year is more important than the
    # month, which is more important than the day

    somme = sum(difference)
    # Now, we just have to do the sum of the list, and see in which case it
    # is. A negative value means date1 is before date2, a positve value means
    # the opposite, and a zero means the dates are the same

    if somme < 0:
        return -1

    elif somme > 0:
        return 1
    else:
        return 0

def parse_fichier_ics(fichier_ics: str):
    """
    Returns all events from an ics file whose path was given
    """
    with open(fichier_ics) as file:
        return [parse_event(event) for event in extract_events(file.read())]

# Programme principal
def main():
    export_markdown(traitement(parse_fichier_ics("data/S1G2.ics"), "S1G2"))



if __name__ == '__main__':
    main()
# Fin

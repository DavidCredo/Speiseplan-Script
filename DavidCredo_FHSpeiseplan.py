# Skript um den heutigen Speiseplan der FH-Kiel Mensa in eine CSV Datei auszugeben.
# Übungsprojekt des IDW Kurses "Automate boring stuff with python"
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# Initialwerte 
url = "https://www.studentenwerk.sh/de/essen/standorte/kiel/schwentinemensa/speiseplan.html"
titel =[]
preis = []

# Funktion die die tableData Elemente mit dem zum Gericht gehörenden Preis sucht
def find_price(e):
    if e.find(string=re.compile("€")):
        return e.find(string=re.compile("€"))

def find_title(e):
    if e.find("td") and find_price(e) != None:
        return e.find("strong").text


HEADERS = ({'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.2228.0 Safari/537.36',
            'Accept-Language': 'de-DE, en;q=0.5'})

results = requests.get(url, headers= HEADERS )

soup = BeautifulSoup(results.text, "html.parser")

#Suchen nach korrekten Table Elementen um nicht sämtliche Gerichte der Woche abzugreifen
today = soup.find("div", class_="day today")
todays_dishes = today.find_all("tr")
# Erstes Table Element ist redundant für die Darstellung und wird aus dem Array entfernt
todays_dishes.pop(0)

# Loop über die Elemente im dishes Array um die Titel und Preis Arrays mit den korrekten Werten zu befüllen
for element in todays_dishes:
    title_temp = find_title(element)
    if title_temp != None:
        titel.append(title_temp)
    else:
        titel.append(None)

    price_element = find_price(element)
    if price_element != None:
        preis.append(price_element)
    else:
        preis.append(None)


def create_data_frame():

    dish_table = pd.DataFrame({
        "Titel": titel,
        "Preis": preis,
    })
# Logik um die leeren Elemente aus dem DataFrame zu löschen.
# Regex um nach leeren Reihen im table zu suchen und die Werte zu ersetzen
    empty_elements = dish_table.copy()
    empty_elements = empty_elements.replace(r'^s*$', float('NaN'), regex = True)
# Ersetzte Werte werden aus dem DataFrame gedroppt
    clean_dish_table = empty_elements.copy()
    clean_dish_table.dropna(inplace = True)

    clean_dish_table.to_csv("Speiseplan.csv")

create_data_frame()

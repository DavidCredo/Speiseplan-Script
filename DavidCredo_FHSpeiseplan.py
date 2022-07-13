# Skript um den heutigen Speiseplan der FH-Kiel Mensa in meine Notion DB geladen.
# Übungsprojekt des IDW Kurses "Automate boring stuff with python"
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import notion_df
import os
from dotenv import load_dotenv
import datetime
notion_df.pandas()
load_dotenv()

notion_api_key = os.getenv('NOTION_API_KEY')
notion_db = os.getenv('NOTION_DB_URL')

# Initialwerte 
HEADERS = ({'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.2228.0 Safari/537.36',
            'Accept-Language': 'de-DE, en;q=0.5'})

today = datetime.date.today().strftime('%Y-%m-%d')
print(today)
url = "https://studentenwerk.sh/de/mensen-in-kiel?ort=1&mensa=5#mensaplan"
titel = []
diet = []
preis = []
results = requests.get(url, headers= HEADERS )
soup = BeautifulSoup(results.text, "html.parser")

# Funktionen die die tableData Elemente mit dem zum Gericht zugehörigen Titel/Preis sucht
def find_price(e):
    if e.find(class_="menu_preis"):
        return e.find(class_="menu_preis").text

def find_title(e):
    if e.find(class_="menu_name"):
        return e.find(class_="menu_name").text

def find_diet(e):
    if e.find("img"):
        return e.find("img")['alt']
#Suchen nach korrekten Table Elementen um nicht sämtliche Gerichte der Woche abzugreifen
def find_todays_dishes():
    todays_date = soup.find(attrs={"class": "tag_headline", "data-day" : today})
    todays_dishes = todays_date.find_all(class_="mensa_menu_detail")
    return todays_dishes

todays_dishes = find_todays_dishes()
# Loop über die Elemente in dishes Array um die Titel und Preis Arrays mit den korrekten Werten zu befüllen
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
    diet_element = find_diet(element)
    if diet_element != None:
        diet.append(diet_element)

def create_data_frame():

    dish_table = pd.DataFrame({
        "Titel": titel,
        "Diet": diet,
        "Preis": preis,
    })
#  leere Elemente aus dem DataFrame löschen.
# Regex um nach leeren Reihen im table zu suchen und die Werte zu ersetzen
    empty_elements = dish_table.copy()
    empty_elements = empty_elements.replace(r'^s*$', float('NaN'), regex = True)
# Ersetzte Werte werden aus dem DataFrame gedroppt
    clean_dish_table = empty_elements.copy()
    clean_dish_table.dropna(inplace = True)

    return clean_dish_table

clean_dish_table = create_data_frame()
# print(clean_dish_table)
notion_df.upload(clean_dish_table, notion_db, title="Playground DB", api_key=notion_api_key)


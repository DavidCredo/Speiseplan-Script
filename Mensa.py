import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime

class Mensa:
    def __init__(self, url):
        self.HEADERS = ({'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.2228.0 Safari/537.36',
            'Accept-Language': 'de-DE, en;q=0.5'})

        self.url = url
        self.diet = []
        self.title = []
        self.price = []
        self.day = datetime.date.today().strftime('%Y-%m-%d')
        self.results = None
        self.soup = None
        self.data_frame = None
        self.jsonPayload = None
        self.todays_dishes = None

    # Funktionen die die tableData Elemente mit dem zum Gericht zugehörigen Titel/Preis sucht
    def parse_html(self):
        self.results = requests.get(self.url, headers = self.HEADERS )
        self.soup = BeautifulSoup(self.results.text, "html.parser")

    def find_price(self, e):
        if e.find(class_="menu_preis"):
            return e.find(class_="menu_preis").text

    def find_title(self, e):
        if e.find(class_="menu_name"):
            return e.find(class_="menu_name").text

    def find_diet(self, e):
        if e.find("img"):
            return e.find("img")['alt']

    #Suchen nach korrekten Table Elementen um nicht sämtliche Gerichte der Woche abzugreifen
    def find_todays_dishes(self):
        if self.soup != None:
            todays_date = self.soup.find(attrs={"class": "tag_headline", "data-day" : self.day})
            self.todays_dishes = todays_date.find_all(class_="mensa_menu_detail")

    # Loop über die Elemente in dishes Array um die Titel und Preis Arrays mit den korrekten Werten zu befüllen

    def create_parsed_array(self):
        for element in self.todays_dishes:
            title_temp = self.find_title(element)
            if title_temp != None:
                self.title.append(title_temp)
            else:
                self.title.append(None)

            price_element = self.find_price(element)
            if price_element != None:
                self.price.append(price_element)
            else:
                self.price.append(None)
            diet_element = self.find_diet(element)
            if diet_element != None:
                self.diet.append(diet_element)

    def create_data_frame(self):
        self.create_parsed_array()

        dish_table = pd.DataFrame({
            "Titel": self.title,
            "Diet": self.diet,
            "Preis": self.price,
        })
    
    #  leere Elemente aus dem DataFrame löschen.
    # Regex um nach leeren Reihen im table zu suchen und die Werte zu ersetzen
        empty_elements = dish_table.copy()
        empty_elements = empty_elements.replace(r'^s*$', float('NaN'), regex = True)
    # Ersetzte Werte werden aus dem DataFrame gedroppt
        clean_dish_table = empty_elements.copy()
        clean_dish_table.dropna(inplace = True)
        self.data_frame = clean_dish_table
        return clean_dish_table

    def get_mensa_data(self):
        self.jsonPayload = self.data_frame.to_json(orient="records")
        return self.jsonPayload

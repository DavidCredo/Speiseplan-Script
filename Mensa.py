import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime


class Mensa:
    def __init__(self, url, day=None):
        self.HEADERS = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.2228.0 Safari/537.36",
            "Accept-Language": "de-DE, en;q=0.5",
        }

        self.url = url
        self.diet = []
        self.title = []
        self.price = []
        self.day = day if day else datetime.datetime.today().strftime("%Y-%m-%d")
        self.results = None
        self.soup = None
        self.data_frame = None
        self.days_dishes = None

    # Funktionen die die tableData Elemente
    #  mit dem zum Gericht zugehörigen Titel/Preis sucht
    def parse_html(self):
        self.results = requests.get(self.url, headers=self.HEADERS)
        self.soup = BeautifulSoup(self.results.text, "html.parser")

    def find_price(self, e: BeautifulSoup):
        if e.find(class_="menu_preis"):
            raw_price = e.find(class_="menu_preis").text
            first_price = raw_price.split(" €")[0]
            return first_price

    def find_title(self, e):
        if e.find(class_="menu_name"):
            return e.find(class_="menu_name").text

    def find_diet(self, e: BeautifulSoup):
        if e.find("img"):
            tags = e.findAll("img")
            diet_label = ""
            for tag in tags:
                if tag["alt"] == "vegan":
                    diet_label = "Vegan"
                    return diet_label
                else:
                    diet_label = "Nicht Vegan"
                    continue
            return diet_label

    # Suchen nach korrekten Table Elementen 
    # um nicht sämtliche Gerichte der Woche abzugreifen
    def find_days_dishes(self):
        if self.soup is not None:
            dishes_for_days_date = self.soup.find(
                attrs={
                    "class": "tag_headline",
                    "data-day": self.day
                }
            )
            self.days_dishes = dishes_for_days_date.find_all(
                class_="mensa_menu_detail"
            )
        else:
            print("Error! No HTML parsed yet!")

    # Loop über die Elemente in dishes Array um die Titel
    #  und Preis Arrays mit den korrekten Werten zu befüllen

    def create_parsed_arrays(self):

        for element in self.days_dishes:
            title_element = self.find_title(element)
            self.title.append(title_element)

            price_element = self.find_price(element)
            self.price.append(price_element)

            diet_element = self.find_diet(element)
            self.diet.append(diet_element)

    def create_data_frame(self):
        self.create_parsed_arrays()

        self.data_frame = pd.DataFrame(
            {
                "Titel": self.title,
                "Diet": self.diet,
                "Preis": self.price,
            }
        )

    def get_mensa_data(self):
        return self.data_frame.to_json(orient="records")

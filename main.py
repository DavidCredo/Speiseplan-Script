from json import loads
from Mensa import Mensa
from flask import Flask, jsonify

app = Flask(__name__)
url = "https://studentenwerk.sh/de/mensen-in-kiel?ort=1&mensa=5#mensaplan"

@app.route('/mensa')
def get_data():
    mensa = Mensa(url)
    mensa.parse_html()
    mensa.find_todays_dishes()
    mensa.create_data_frame()
    payload = loads(mensa.get_mensa_data())

    if payload == []:
        return jsonify({"message": "No data found"}), 404
    else:
        return jsonify(payload)
    
@app.route('/mensa/<day>')
def get_day_data(day):
    mensa = Mensa(url, day)
    mensa.parse_html()
    mensa.find_days_dishes()
    mensa.create_data_frame()
    payload = loads(mensa.get_mensa_data())

    if payload == []:
        return jsonify({"message": "No data found"}), 404
    else:
        return jsonify(payload)

if __name__ == '__main__':
    app.run(port=8000, debug=True)


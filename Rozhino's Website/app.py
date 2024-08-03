from flask import Flask, jsonify, render_template, request
from skyfield.api import Star, load, N, E, wgs84
from skyfield.data import hipparcos
from datetime import datetime
from pytz import timezone
import time

app = Flask(__name__)

iraq_time = timezone('Asia/Baghdad')
ts = load.timescale()

planets = load('de421.bsp')
earth = planets['earth']

with load.open(hipparcos.URL) as f:
    df = hipparcos.load_dataframe(f)

with open('stars.txt', 'r') as file:
    stars_from_file = {line.split(': ')[0]: line.split(': ')[1].strip() for line in file}

with open('solar_system_bodies.txt', 'r') as file:
    solar_system_bodies_from_file = {line.split(': ')[0]: line.split(': ')[1].strip() for line in file}


def initialize():
    current_timestamp = time.time()
    struct_time = time.localtime(current_timestamp)

    year, month, day, hour, minute, second = struct_time[:6]

    d = datetime(year, month, day, hour, minute, second)
    e = iraq_time.localize(d)
    t = ts.from_datetime(e)

    dt = t.astimezone(iraq_time)
    suli = earth + wgs84.latlon(35.566551 * N, 45.386761 * E, elevation_m=804)

    return t, dt, suli


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/tutorials")
def tutorials():
    return render_template("tutorials.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/antikythera", methods=['GET'])
def antikythera():
    user_input = request.args.get('celestial_body').title()
    print(f"User input: {user_input}")
    print(f"Received GET request for celestial body: {user_input}")

    t, dt, suli = initialize()

    if user_input in stars_from_file:
        input_star = Star.from_dataframe(df.loc[int(stars_from_file[f'{user_input}'])])

    else:
        input_star = planets[solar_system_bodies_from_file[f'{user_input}']]

    print(f"{input_star}")
    astro = suli.at(t).observe(input_star)
    apparent = astro.apparent()

    alt, az, distance = apparent.altaz()

    location = {
        "azimuth": az.degrees,
        "altitude": alt.degrees,
        "distance": distance.km,
        "something": 'AST: ' + str(dt)
    }

    return jsonify(location)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

# antikythera?celestial_body=sun

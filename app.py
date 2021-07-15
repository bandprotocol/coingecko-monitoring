import requests
import json
import os

from flask import Flask, jsonify
from flask_apscheduler import APScheduler

# from notification.pager_duty import send_incident, catch_incident

app = Flask(__name__)
app.config["DEBUG"] = True


@app.route("/monitor_slugs", methods=["GET"])
# @catch_incident
def slugs_is_working():
    try:
        f = open('slugs_monitor.json',)
        data = json.load(f)
        slugs_str = ",".join(list(data.get("SLUGS_MONITOR").values()))
        slugs = slugs_str.split(',')
        prices = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": slugs_str, "vs_currencies": "USD"},
        ).json()

        if len(slugs) != len(prices):
            error_slugs = []
            for slug in slugs:
                check = prices.get(slug)
                if check is None:
                    error_slugs.append(slug)

            # send_incident(
            #     "Can't get some slug on coingecko", f"slugs {error_slugs} is failure")

            return f"Can't get some slug on coingecko --> {error_slugs} is failure"

    except json.decoder.JSONDecodeError:
        # send_incident(
        #     Can't docode json, There was a problem accessing the json data)
        return "Can't docode json, There was a problem accessing the json data"

    return "everything good"


app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

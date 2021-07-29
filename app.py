import os
import requests
import json

from flask import Flask

from notification.pager_duty import send_incident

app = Flask(__name__)
app.config["DEBUG"] = True


@app.route("/", methods=["GET"])
def slugs_is_working():
    try:
        url = "https://raw.githubusercontent.com/bandprotocol/coingecko-monitoring/master/slugs.json"
        response = requests.get(url)
        data = response.json()
        slugs_str = ",".join(list(data.values()))
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

            send_incident(
                "Can't get some slug on coingecko", f"slugs {error_slugs} is failure")

            return f"Can't get some slug on coingecko --> {error_slugs} is failure"

        return ""

    except Exception as e:
        send_incident("Slugs monitoring error", str(e))
        return f"Slugs monitoring error, {str(e)}", 500


app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

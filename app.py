import os
import requests

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
        slugs = list(data.values())
        prices = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": ",".join(slugs), "vs_currencies": "USD"},
        ).json()

        if len(slugs) != len(prices):
            error_slugs = []
            for slug in slugs:
                print(slug)
                check = prices.get(slug)
                if check is None:
                    error_slugs.append(slug)

            send_incident(
                "Can't get some slug on coingecko", f"slugs {error_slugs} is failure", high=False)

            return f"Can't get some slug on coingecko --> {error_slugs} is failure"

        return ""

    except Exception as e:
        send_incident("Slugs monitoring error", str(e), high=False)
        return f"Slugs monitoring error, {str(e)}", 500

app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
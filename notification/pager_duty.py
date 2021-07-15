import requests
import traceback
import hashlib
from functools import wraps

from .config import API_TOKEN, ROUTING_KEY, SOURCE


EXCEPTION_RAISED = "Exception raised"


def catch_incident(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            send_incident(
                EXCEPTION_RAISED,
                f"{f.__name__}: Process raised execption with stack trace :{traceback.format_exc()}",
            )
            # Rethrow exception to main process
            raise e

    return wrap


def send_incident(title, details, high=True):
    dedup = SOURCE + "." + title
    if title == EXCEPTION_RAISED:
        dedup += "." + details
    print(f"{title}: {details}", flush=True)
    requests.post(
        url="https://events.pagerduty.com/v2/enqueue",
        headers={
            "Authorization": f"Token token={API_TOKEN}",
            "From": "app@bandprotocol.com",
            "Content-Type": "application/json",
            "Accept": "application/vnd.pagerduty+json;version=2",
        },
        json={
            "payload": {
                "summary": SOURCE + ": " + title,
                "custom_details": details,
                "severity": "critical" if high else "warning",
                "source": SOURCE,
            },
            "event_action": "trigger",
            "routing_key": ROUTING_KEY,
            "dedup_key": hashlib.md5(dedup.encode()).hexdigest(),
        },
    ).json()

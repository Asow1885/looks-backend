import requests
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("AIzaSyBqS4ATuaN5BHKgmLTmAFBi1osN836k9mY")

def get_live_traffic_factor(origin, destination):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "departure_time": "now",
        "key": GOOGLE_API_KEY,
    }

    response = requests.get(url, params=params)
    data = response.json()

    try:
        leg = data["routes"][0]["legs"][0]
        duration = leg["duration"]["value"]
        traffic_duration = leg["duration_in_traffic"]["value"]

        if duration == 0:
            return 1.0

        return round(traffic_duration / duration, 2)
    except Exception as e:
        print(f"Traffic API error: {e}")
        return 1.0  # fallback

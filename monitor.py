import json
import os
import re
from datetime import datetime

import requests

SHOWTIME_URL = (
    "https://www.amctheatres.com/movie-theatres/"
    "san-francisco/amc-metreon-16/showtimes"
)

MOVIE_NAME = "The Odyssey"

DISCORD_WEBHOOK = os.environ["DISCORD_WEBHOOK"]

HEADERS = {
    "User-Agent":
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
}


def get_html():
    r = requests.get(
        SHOWTIME_URL,
        headers=HEADERS,
        timeout=20,
    )
    r.raise_for_status()
    return r.text


def find_dates(html):
    """
    提取网页中的所有 YYYY-MM-DD
    """
    dates = set(
        re.findall(r"20\d\d-\d\d-\d\d", html)
    )

    valid = []

    for d in dates:
        try:
            datetime.strptime(d, "%Y-%m-%d")
            valid.append(d)
        except ValueError:
            pass

    return sorted(valid)


def load_state():
    if not os.path.exists("state.json"):
        return {}

    with open("state.json") as f:
        return json.load(f)


def save_state(state):
    with open("state.json", "w") as f:
        json.dump(state, f)


def notify(message):
    requests.post(
        DISCORD_WEBHOOK,
        json={"content": message},
        timeout=20,
    )


def main():
    html = get_html()

    if MOVIE_NAME.lower() not in html.lower():
        print("Movie not found")
        return

    dates = find_dates(html)

    if not dates:
        print("No dates")
        return

    newest = max(dates)

    state = load_state()

    old = state.get("latest_date")

    print("Current latest:", newest)
    print("Previous:", old)

    if old is None:
        state["latest_date"] = newest
        save_state(state)
        print("Initialized.")
        return

    if newest > old:

        notify(
            f"🎬 AMC Metreon released NEW Odyssey IMAX showtimes!\n"
            f"Old latest: {old}\n"
            f"New latest: {newest}\n\n"
            f"{SHOWTIME_URL}"
        )

        state["latest_date"] = newest
        save_state(state)

        print("Notification sent!")

    else:
        print("No change.")


if __name__ == "__main__":
    main()
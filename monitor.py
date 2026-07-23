import requests
import smtplib
import json
import os

from bs4 import BeautifulSoup
from email.message import EmailMessage


URL = "https://www.amctheatres.com/movie-theatres/san-francisco/amc-metreon-16/showtimes"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

GMAIL_ADDRESS = "manhengwang2001@gmail.com"

GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]

STATE_FILE = "last_seen.json"


def get_odyssey_imax70mm():

    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    section = soup.find(
        "li",
        attrs={
            "aria-label": "IMAX 70MM Showtimes"
        }
    )

    if not section:
        return []


    shows = []

    for button in section.find_all("a"):

        time = button.find("time")

        if not time:
            continue

        shows.append(
            {
                "time": time.text.strip(),
                "link": button.get("href"),
                "status": button.get_text(" ", strip=True)
            }
        )

    return shows



def load_previous():

    if not os.path.exists(STATE_FILE):
        return []

    with open(STATE_FILE, "r") as f:
        return json.load(f)



def save_current(shows):

    with open(STATE_FILE, "w") as f:
        json.dump(
            shows,
            f,
            indent=2
        )



def send_email(new_shows):

    msg = EmailMessage()

    msg["Subject"] = "🎬 New AMC Odyssey IMAX 70MM Showtime"

    msg["From"] = GMAIL_ADDRESS
    msg["To"] = GMAIL_ADDRESS


    body = "New IMAX 70MM showtimes found:\n\n"


    for show in new_shows:

        body += (
            f"{show['status']}\n"
            f"https://www.amctheatres.com{show['link']}\n\n"
        )


    msg.set_content(body)


    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465
    ) as smtp:

        smtp.login(
            GMAIL_ADDRESS,
            GMAIL_APP_PASSWORD
        )

        smtp.send_message(msg)



if __name__ == "__main__":


    shows = get_odyssey_imax70mm()


    previous = load_previous()


    new_shows = [
        show
        for show in shows
        if show not in previous
    ]


    if new_shows:

        print("New shows found:")
        print(new_shows)

        send_email(new_shows)

    else:

        print("No new shows")


    save_current(shows)
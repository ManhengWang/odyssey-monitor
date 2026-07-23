import requests
import smtplib
import os
from bs4 import BeautifulSoup
from email.message import EmailMessage


URL = "https://www.amctheatres.com/movie-theatres/san-francisco/amc-metreon-16/showtimes"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


GMAIL_ADDRESS = "manhengwang2001@gmail.com"

GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]


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
                "datetime": time.get("datetime"),
                "link": button.get("href"),
                "status": button.get_text(" ", strip=True)
            }
        )


    return shows



def send_email(shows):

    msg = EmailMessage()

    msg["Subject"] = "🎬 AMC The Odyssey IMAX 70MM Alert"
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = GMAIL_ADDRESS


    body = "Found IMAX 70MM shows:\n\n"

    for show in shows:
        body += (
            f"{show['status']}\n"
            f"{show['link']}\n\n"
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


    print(shows)


    if shows:
        send_email(shows)
        print("Email sent!")

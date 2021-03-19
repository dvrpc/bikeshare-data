"""
scrape.py
---------

This script finds all of the CSV files on the
Indego data page. It then opens the link to each
in a web browser to automate the download.

After the script finishes, copy the CSV files
from your downloads folder to a better place.

Note: Stations and trips require different processes
since trips come as ZIP files while stations is a 
non-zipped CSV file.
"""

from bs4 import BeautifulSoup
import requests
import webbrowser
import pandas as pd
import csv
from pathlib import Path

DATA_URL = "https://www.rideindego.com/about/data/"


def _get_soup(url: str) -> BeautifulSoup:
    """
    Connect to URL with requests/bs4
    Headers are needed to prevent a 403 response
    """

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:86.0) Gecko/20100101 Firefox/86.0"
    }
    page = requests.get(url, headers=headers)

    return BeautifulSoup(page.content, "html.parser")


def trips():
    """
    Download the TRIP csv files (one per quarter per year)
    to your Downloads folder
    """

    soup = _get_soup(DATA_URL)

    data_list = soup.find("section", class_="entry-content").find_next("ul").find_all("a")
    href_list = [a["href"] for a in data_list]

    for url in href_list:
        webbrowser.open(url)


if __name__ == "__main__":
    trips()

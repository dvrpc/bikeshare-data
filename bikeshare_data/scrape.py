"""
scrape.py
---------

This script finds all of the CSV files on the
Indego data page. It then opens the link to each
in a web browser to automate the download.

After the script finishes, copy the CSV files
from your downloads folder to a better place.
"""

import bs4
import requests
import webbrowser
import pandas as pd
import csv
from pathlib import Path

DATA_URL = "https://www.rideindego.com/about/data/"


def _get_soup(url):
    """
    Connect to URL with requests/bs4
    Headers are needed to prevent a 403 response
    """

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:86.0) Gecko/20100101 Firefox/86.0"
    }
    page = requests.get(url, headers=headers)
    soup = bs4.BeautifulSoup(page.content, "html.parser")

    return soup


def stations():
    soup = _get_soup(DATA_URL)

    print("-> Downloading STATION data")

    station_info_tag = None
    for x in soup.find_all("h1"):
        if "Information" in x.text:
            station_info_tag = x

    station_csv_url = station_info_tag.find_next("ul").find_next("a")["href"]

    station_soup = _get_soup(station_csv_url)
    station_text = station_soup.text.split("\r\n")

    data = [x for x in list(csv.reader([y for y in station_text], delimiter=",", quotechar='"'))]

    df = pd.DataFrame(data[1:])
    df.columns = data[0]

    df.dropna(inplace=True)
    df.to_csv(Path.home() / "Downloads" / "stations.csv")


def trips():
    """
    Download the TRIP csv files (one per quarter per year)
    """
    soup = _get_soup(DATA_URL)

    print("-> Downloading TRIP data")

    data_list = soup.find("section", class_="entry-content").find_next("ul").find_all("a")
    href_list = [a["href"] for a in data_list]

    for url in href_list:
        webbrowser.open(url)


def main():
    stations()
    trips()


if __name__ == "__main__":
    main()

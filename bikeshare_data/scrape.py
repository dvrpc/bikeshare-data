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
import geopandas as gpd
from shapely.geometry import shape

from bikeshare_data.helpers import _import_gdf

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


def station_csv():
    """
    Download Station data to a single CSV file
    named "stations.csv", within your Downloads folder
    """

    soup = _get_soup(DATA_URL)

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

    outpath = Path.home() / "Downloads" / "stations.csv"

    df.to_csv(outpath, index=False)


def station_geojson():
    res = requests.get("https://kiosks.bicycletransit.workers.dev/phl.geojson")
    data = res.json()
    for d in data["features"]:
        d["geometry"] = shape(d["geometry"])
        for k in d["properties"]:
            d[k] = d["properties"][k]
        del d["properties"]
        d["bikes"] = str(d["bikes"])
    gdf = gpd.GeoDataFrame(data["features"]).set_geometry("geometry")
    gdf.set_crs(epsg=4326, inplace=True)

    _import_gdf(gdf, "station_shapes", "Point")


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


def main():
    """Download station and trip files"""
    # station_csv()
    station_geojson()
    # trips()


if __name__ == "__main__":
    main()

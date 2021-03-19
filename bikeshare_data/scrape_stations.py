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

import requests
import geopandas as gpd
from shapely.geometry import shape

from bikeshare_data import DEFAULT_DB_URI
from bikeshare_data.helpers import _import_gdf


def station_geojson(uri: str = DEFAULT_DB_URI) -> None:
    """
    Download JSON data from the realtime station feed,
    convert to geodataframe, then import to SQL
    """
    res = requests.get("https://kiosks.bicycletransit.workers.dev/phl.geojson")
    data = res.json()

    # Clean up attributes for a clean table
    for d in data["features"]:
        d["geometry"] = shape(d["geometry"])
        for k in d["properties"]:
            d[k] = d["properties"][k]
        del d["properties"]
        d["bikes"] = str(d["bikes"])

    # Turn JSON into geodataframe
    gdf = gpd.GeoDataFrame(data["features"]).set_geometry("geometry")
    gdf.set_crs(epsg=4326, inplace=True)

    # Import to SQL
    _import_gdf(gdf, "station_shapes", "Point", uri=uri)


if __name__ == "__main__":
    station_geojson()

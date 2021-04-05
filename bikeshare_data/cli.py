from os import stat
import click
from bikeshare_data.scrape_trips import trips
from bikeshare_data.scrape_stations import station_geojson
from bikeshare_data.import_to_sql import main as _import
from bikeshare_data.analyze_trips import analyze_trips as _analyze_trips


@click.group()
def main():
    """indego is a command-line-utility for downloading and analyzing bikeshare data"""
    pass


@main.command()
def scrape_trips():
    """Download trip data as CSVs from Indego's website"""
    trips()


@main.command()
def scrape_stations():
    """Import station geojson directly to SQL"""
    station_geojson()


@main.command()
def import_to_sql():
    """Import CSV files to PostgreSQL"""
    _import()


@main.command()
def analyze():
    """Analyze trip patterns for selected stations """
    _analyze_trips()
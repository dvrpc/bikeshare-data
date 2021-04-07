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
@click.option(
    "--include-inactive", "-i", is_flag=True, help="Flag to include inactive kiosks in analysis"
)
@click.option("--write", "-w", is_flag=True, help="Flag to write output .xlsx files")
def analyze(include_inactive, write):
    """Analyze trip patterns for selected stations """
    _analyze_trips(write_output_files=write, include_inactive_stations=include_inactive)
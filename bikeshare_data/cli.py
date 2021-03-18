import click
from bikeshare_data.scrape import main as _scrape
from bikeshare_data.import_to_sql import main as _import


@click.group()
def main():
    """indego is a command-line-utility for downloading and analyzing bikeshare data"""
    pass


@main.command()
def scrape():
    """Download CSV files from Indego's website"""
    _scrape()


@main.command()
def import_to_sql():
    """Import CSV files to PostgreSQL"""
    _import()

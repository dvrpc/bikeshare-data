import click
from bikeshare_data.scrape import main as _scrape


@click.group()
def main():
    """indego is a command-line-utility for downloading and analyzing bikeshare data"""
    pass


@main.command()
def scrape():
    """Download CSV files from Indego's website"""
    _scrape()

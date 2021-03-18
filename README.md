# bikeshare-data

Python module to facilitate the acquisition and analysis of Indego bikeshare data

## Usage

1. Download all CSV files with: `indego scrape`
2. Move these files from your download folder to a better spot
3. Import the CSV files to PostgreSQL with: `indego import-to-sql`

TODO:

4. Aggregate trips based upon an input polygon shapefile

## Development

Create a virtual environment using `conda`:

```
conda env create -f environment.yml
```

Activate the environment:

```
conda activate bikeshare-data
```

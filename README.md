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

## Notes

```
<script src="https://cdn.rawgit.com/mapbox/wellknown/master/wellknown.js"></script>


let my_wkt = wellknown.stringify(data.features[0].geometry);
```

This returns something like:

```
POLYGON ((-91.8466200103753 42.76567129175277, -91.87048094177136 42.75911775240124, -91.86721937560942 42.7526895693039, -91.83185713195711 42.75621885041684, -91.8466200103753 42.76567129175277))
```

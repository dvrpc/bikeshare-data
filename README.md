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

Create a `.env` file to store configuration parameters:

```
DEFAULT_DB_URI = postgresql://postgres:password@localhost:5432/indego
DEFAULT_DATA_FOLDER = /path/to/data/dir
STUDY_AREA = "ST_SetSRID(ST_GeomFromText('POLYGON((-75.179070999792 39.9561219999082, ...etc...))'), 4326)"
```

## Usage

### 1) Download all CSV files hosted on [Indego's data page](https://www.rideindego.com/about/data/):

```
indego scrape-trips
```

This will download all CSV files to your computer's `Downloads` folder. Cut and paste these files into the `DEFAULT_DATA_FOLDER` before continuing to the next step.

### 2 ) To import the CSV files into SQL, run:

```
indego import-to-sql
```

### 3) Load the authoritative station geojson file directly to SQL with:

```
indego scrape-stations
```

## Notes

The study area boundary is defined using WKT to facilitate future integration into a backend API that will communicate with a webmap frontend where users point/click to define a custom study area.

```
<script src="https://cdn.rawgit.com/mapbox/wellknown/master/wellknown.js"></script>


let my_wkt = wellknown.stringify(data.features[0].geometry);
```

This returns something like:

```
POLYGON ((-91.8466200103753 42.76567129175277, -91.87048094177136 42.75911775240124, -91.86721937560942 42.7526895693039, -91.83185713195711 42.75621885041684, -91.8466200103753 42.76567129175277))
```

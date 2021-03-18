from pathlib import Path
import pandas as pd

from bikeshare_data import DEFAULT_DATA_FOLDER
from bikeshare_data.helpers import _import_df, _execute_query


def csv_to_postgres(data_folder: Path = DEFAULT_DATA_FOLDER) -> None:
    """
    Import all CSV files within data_folder to postgres
    """

    trip_dfs = []

    for f in data_folder.glob("*.csv"):
        if f.name == "stations.csv":
            df = pd.read_csv(f)
            _import_df(df, "stations", if_exists="replace")
        else:
            print("Reading", f.name)
            df = pd.read_csv(f)
            trip_dfs.append(df)

    all_trips_df = pd.concat(trip_dfs, ignore_index=True)
    _import_df(all_trips_df, "raw_trips", if_exists="replace")


def sql_manipulations():

    queries = [
        # enable PostGIS
        """
            CREATE EXTENSION IF NOT EXISTS postgis;
        """,
        """
            DROP TABLE IF EXISTS trips CASCADE;
            CREATE TABLE trips AS TABLE raw_trips;
        """,
        # Start Station ID column name changed over time...
        # ... this gets it all into one column
        """
            UPDATE trips
            SET start_station = start_station_id
            WHERE start_station IS NULL;
        """,
        # Same for End Station ID column
        """
            UPDATE trips
            SET end_station = end_station_id
            WHERE end_station IS NULL;
        """,
        # Add geom columns for start and end of trip
        """
            ALTER TABLE trips
            DROP COLUMN IF EXISTS start_geom;
            
            ALTER TABLE trips
            ADD COLUMN start_geom geometry(Point, 4326);
        """,
        """
            ALTER TABLE trips
            DROP COLUMN IF EXISTS end_geom;
            
            ALTER TABLE trips
            ADD COLUMN end_geom geometry(Point, 4326);
        """,
        # Update geom columns to hold a point for start/end
        """
            UPDATE trips
            SET start_geom = 
            ST_SetSRID(
                ST_MakePoint(
                    round(start_lon::numeric, 5),
                    round(start_lat::numeric, 5)
                ),
                4326
            )
            WHERE start_station_id > 3000 AND start_station_id < 9000;
        """,
        """
            UPDATE trips
            SET end_geom = 
            ST_SetSRID(
                ST_MakePoint(
                    round(end_lon::numeric, 5),
                    round(end_lat::numeric, 5)
                ),
                4326
            )
            WHERE end_station_id > 3000 AND end_station_id < 9000;
        """,
    ]
    for q in queries:
        _execute_query(q)


def main():
    # csv_to_postgres()
    sql_manipulations()


if __name__ == "__main__":
    main()

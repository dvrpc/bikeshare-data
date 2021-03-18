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
        # Start Station ID column name changed over time...
        # ... this gets it all into one column
        """
            UPDATE trips 
            SET start_station_id = start_station
            WHERE start_station_id IS NULL;
        """,
        # Same for End Station ID column
        """
            UPDATE trips 
            SET end_station_id = end_station
            WHERE end_station_id IS NULL;
        """,
        # Add geom columns for start and end of trip
        """
            ALTER TABLE trips
            ADD COLUMN start_geom geometry(Point, 4326);
        """,
        """
            ALTER TABLE trips
            ADD COLUMN end_geom geometry(Point, 4326);
        """,
        # Update geom columns to hold a point for start/end
        """
            UPDATE trips
            SET start_geom = 
            ST_SetSRID(
                ST_MakePoint(
                    start_lon::float,
                    start_lat::float
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
                    end_lon::float,
                    end_lat::float
                ),
                4326
            )
            WHERE end_station_id > 3000 AND end_station_id < 9000;
        """,
        # Create a view with trip records that have start and end geoms...
        # ... since not all of them have usable lat/lon on both trip ends
        """
            DROP VIEW IF EXISTS trips_w_geom;
            CREATE VIEW trips_w_geom AS
                SELECT *
                FROM trips
                WHERE start_geom IS NOT NULL
                    AND end_geom IS NOT NULL
        """,
    ]
    for q in queries:
        _execute_query(q)


def main():
    csv_to_postgres()
    sql_manipulations()


if __name__ == "__main__":
    main()

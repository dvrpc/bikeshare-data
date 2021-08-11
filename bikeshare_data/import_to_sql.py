from pathlib import Path
import pandas as pd

from bikeshare_data import DEFAULT_DATA_FOLDER
from bikeshare_data.helpers import _import_df, _execute_query


def csv_to_postgres(data_folder: Path = DEFAULT_DATA_FOLDER) -> None:
    """
    Import all CSV files within data_folder to postgres
    """

    trip_dfs = []

    # Read all csv files, including those nested in sub-folders
    for f in data_folder.rglob("*.csv"):

        # If the word 'stations' shows up in the filename,
        # import it as its own table named 'stations'
        if "stations" in str(f.name).lower():
            df = pd.read_csv(f)
            df["src_file"] = f.stem
            _import_df(df, "stations", if_exists="replace")
        # Otherwise, assume it's a trip file that will get
        # merged into one mega table with all other trip files
        else:
            print("Reading", f.name)
            df = pd.read_csv(f)
            df["src_file"] = f.stem
            trip_dfs.append(df)

    # After reading all files, merge them into one table and import to SQL
    all_trips_df = pd.concat(trip_dfs, ignore_index=True)
    _import_df(all_trips_df, "raw_trips", if_exists="replace")


def sql_manipulations():
    """
    Execute a series of data-prep SQL statements
    """

    queries = [
        # enable PostGIS
        """
            CREATE EXTENSION IF NOT EXISTS postgis;
        """,
        # make a copy of the raw table that omits trips starting
        # or ending at non-station station IDs
        # https://www.rideindego.com/about/data/
        """
            DROP TABLE IF EXISTS trips CASCADE;
            CREATE TABLE trips AS (
                SELECT * FROM raw_trips
                WHERE (end_station > 3000
                  AND end_station < 9000
                  AND start_station > 3000
                  AND start_station < 9000)
                OR (end_station_id > 3000
                  AND end_station_id < 9000
                  AND start_station_id > 3000
                  AND start_station_id < 9000)
            );
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
    ]
    for q in queries:
        _execute_query(q)


def main():
    csv_to_postgres()
    sql_manipulations()


if __name__ == "__main__":
    main()

from pathlib import Path
import psycopg2
import sqlalchemy
from pandas import DataFrame, read_csv, concat
from datetime import datetime

DB_URI = "postgresql://aaron:password@localhost:5432/indego"
DATA_FOLDER = Path("/Volumes/GoogleDrive/My Drive/projects/bikeshare-data")


def _execute_query(sql: str, uri: str = DB_URI) -> None:
    """
    Use psycopg2 to execute + commit an arbitrary SQL query in the database
    """

    connection = psycopg2.connect(uri)
    cursor = connection.cursor()

    cursor.execute(sql)

    cursor.close()
    connection.commit()
    connection.close()


def _import_df(df: DataFrame, sql_tablename: str, if_exists: str, uri: str = DB_URI) -> None:
    """
    Use pandas and sqlalchemy to import a CSV file into a SQL table
    """

    # Ensure column names are all lower-case
    df.columns = [x.lower() for x in df.columns]

    print("Importing dataframe with", df.shape[0], "rows to", sql_tablename)
    print("\t -> Starting at", datetime.now())

    engine = sqlalchemy.create_engine(uri)

    df.to_sql(sql_tablename, engine, if_exists=if_exists)

    engine.dispose()
    print("\t -> Ended at", datetime.now())


def csv_to_postgres(data_folder: Path = DATA_FOLDER) -> None:
    """
    Import all CSV files within data_folder to postgres
    """

    trip_dfs = []

    for f in data_folder.glob("*.csv"):
        if f.name == "stations.csv":
            df = read_csv(f)
            _import_df(df, "stations", if_exists="replace")
        else:
            print("Reading", f.name)
            df = read_csv(f)
            trip_dfs.append(df)

    all_trips_df = concat(trip_dfs, ignore_index=True)
    _import_df(all_trips_df, "trips", if_exists="replace")


def sql_manipulations():
    _execute_query("CREATE EXTENSION IF NOT EXISTS postgis;")


def main():
    csv_to_postgres()


if __name__ == "__main__":
    main()

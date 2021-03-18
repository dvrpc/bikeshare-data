from pathlib import Path
import psycopg2
import sqlalchemy
from pandas import DataFrame
from datetime import datetime
import geopandas as gpd
from geoalchemy2 import WKTElement, Geometry

from bikeshare_data import DEFAULT_DB_URI


def _execute_query(sql: str, uri: str = DEFAULT_DB_URI) -> None:
    """
    Use psycopg2 to execute + commit an arbitrary SQL query in the database
    """

    print(sql)

    connection = psycopg2.connect(uri)
    cursor = connection.cursor()

    cursor.execute(sql)

    cursor.close()
    connection.commit()
    connection.close()


def _import_df(
    df: DataFrame, sql_tablename: str, if_exists: str, uri: str = DEFAULT_DB_URI
) -> None:

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


def _import_polygon_shapefile(
    polygon_shp_path: Path, sql_tablename: str = "study_area", uri: str = DEFAULT_DB_URI
) -> None:
    gdf = gpd.read_file(polygon_shp_path)

    gdf.columns = [x.lower() for x in gdf.columns]
    epsg_code = int(str(gdf.crs).split(":")[1])

    gdf["geom"] = gdf["geometry"].apply(lambda x: WKTElement(x.wkt, srid=epsg_code))
    gdf.drop("geometry", 1, inplace=True)

    engine = sqlalchemy.create_engine(uri)
    gdf.to_sql(
        sql_tablename,
        engine,
        dtype={"geom": Geometry("POLYGON", srid=epsg_code)},
    )
    engine.dispose()
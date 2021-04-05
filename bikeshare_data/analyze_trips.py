import pandas as pd
from bikeshare_data import STUDY_AREA, DEFAULT_DATA_FOLDER
from bikeshare_data.helpers import _get_query_result, _get_gdf, _get_df


def mega_query(study_area_station_list: str):
    """
    Provide a SQL-valid list of station IDs. e.g. (3001, 3002, 3003)

    The query will return the number of inbound, outbound, and internal
    trips for the list of stations, broken out by year and month.
    """

    q = f"""
    with
    station_meta as (
        select
            id as station_id,
            name as station_name,
            addressstreet as station_address
        from station_shapes
        where
            id in {study_area_station_list}
    ),
    internal_trips as (
        select
            end_station as station_id,
            extract(year from start_time::timestamp) as y,
            extract(month from start_time::timestamp) as m,
            count(trip_id) as trips,
            'internal' as trip_type
        from
            trips 
        where
            start_station in {study_area_station_list}
        and
            end_station in {study_area_station_list}
        group by
            end_station, 
            extract(year from start_time::timestamp),
            extract(month from start_time::timestamp)
    ),
    inbound_trips as (
        select
            end_station as station_id,
            extract(year from start_time::timestamp) as y,
            extract(month from start_time::timestamp) as m,
            count(trip_id) as trips,
            'inbound' as trip_type
        from
            trips 
        where
            start_station NOT in {study_area_station_list}
        and
            end_station in {study_area_station_list}
        group by
            end_station, 
            extract(year from start_time::timestamp),
            extract(month from start_time::timestamp)
    ),
    outbound_trips as (
        select
            start_station as station_id,
            extract(year from start_time::timestamp) as y,
            extract(month from start_time::timestamp) as m,
            count(trip_id) as trips,
            'outbound' as trip_type
        from
            trips 
        where
            start_station in {study_area_station_list}
        and
            end_station NOT in {study_area_station_list}
        group by
            start_station, 
            extract(year from start_time::timestamp),
            extract(month from start_time::timestamp)
    ),
    joined_data as (
        select * from internal_trips
        union
        select * from inbound_trips
        union
        select * from outbound_trips
    )
    select
        jd.*,
        sm.station_name,
        sm.station_address
    from
        joined_data jd
    left join
        station_meta sm on sm.station_id = jd.station_id
    """

    df = _get_df(q)

    return df


def analyze_trips(study_area: str = STUDY_AREA):
    """
    Provide a WKT definition of the study area as a string.
    E.g.: "ST_SetSRID(ST_GeomFromText('POLYGON((-75.179070999792 39.9561219999082, ...etc...))'), 4326)"

    This function will then write two XLSX files:
        - total number of trips by station and year (one tab)
        - station-level numbers for inbound, outbound, and internal trips,
          broken out by year and month (one tab per station)
    """

    # Get a list of station IDs within study area
    query = f"""
        SELECT id FROM station_shapes
                WHERE st_within(geom, ({STUDY_AREA}))
        """

    sa_ids = _get_query_result(query)
    sa_ids = str(tuple([x[0] for x in sa_ids]))

    print("Analyzing trips for station IDs:", sa_ids)

    df = mega_query(sa_ids)

    # Write an excel file with a single table, annual ridership by station
    with pd.ExcelWriter("station_summary.xlsx") as writer:

        station_summary = df.pivot_table(
            index=["y"], columns=["station_name"], values="trips", aggfunc="sum"
        ).T
        station_summary.to_excel(writer, sheet_name="raw")

    # Write an excel file with one tab per station
    with pd.ExcelWriter("station_details.xlsx") as writer:

        for station_id in df.station_id.unique():
            filtered_df = df[df["station_id"] == station_id]
            filtered_df.pivot(index=["y", "m"], columns=["trip_type"], values="trips").T.to_excel(
                writer, sheet_name=f"trips_{int(station_id)}"
            )

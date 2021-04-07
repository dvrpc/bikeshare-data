from pathlib import Path
import pandas as pd

from bikeshare_data import STUDY_AREA
from bikeshare_data.helpers import _get_query_result, _get_df


def _station_ids_from_active_kiosk_table(study_area_wkt: str = STUDY_AREA) -> list:
    query = f"""
        SELECT id FROM station_shapes
                WHERE st_within(geom, ({study_area_wkt}))
        """

    return [x[0] for x in _get_query_result(query)]


def _station_ids_from_trip_table(study_area_wkt: str = STUDY_AREA) -> list:
    query = f"""
        with rounded_data as (
            select
                start_station::int as station_id,
                round(start_lon::numeric, 5) as lon,
                round(start_lat::numeric, 5) as lat
            from
                trips
            group by
                start_station,
                round(start_lon::numeric, 5),
                round(start_lat::numeric, 5)
        ),
        geo_data as (
            select
                station_id,
                st_setsrid(st_point(lon, lat), 4326) as geom
            from
                rounded_data
        )
        select distinct station_id
        from geo_data
        where st_intersects(geom, {study_area_wkt})
    """

    return [x[0] for x in _get_query_result(query)]


def _there_are_inactive_stations(
    existing_station_list: list, trip_table_station_list: list
) -> bool:

    ids_to_warn_about = set(trip_table_station_list).difference(set(existing_station_list))

    if ids_to_warn_about:
        print("WARNING!")
        print("The following station IDs used to exist in the study area:")
        for id_val in ids_to_warn_about:
            print("\t ->", id_val)

        return True

    else:
        return False


def _get_station_ids_from_wkt(
    study_area_wkt: str = STUDY_AREA, include_inactive_stations: bool = True
) -> str:
    """
    Get a list of station IDs within study area

    Return as a string that will subsequently be passed into SQL.

    Warn users if they have inactive stations in their study area
    """

    ids_from_trip_table = _station_ids_from_trip_table(study_area_wkt)

    if include_inactive_stations:
        return str(tuple(ids_from_trip_table))

    else:
        ids_from_spatial_table = _station_ids_from_active_kiosk_table(study_area_wkt)

        if _there_are_inactive_stations(ids_from_spatial_table, ids_from_trip_table):
            print("Consider including inactive stations in the analysis!")

        return str(tuple(ids_from_spatial_table))


def _mega_query(study_area_station_list: str):
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


def analyze_trips(
    study_area: str = STUDY_AREA,
    write_output_files: bool = False,
    include_inactive_stations: bool = True,
):
    """
    Provide a WKT definition of the study area as a string.
    E.g.: "ST_SetSRID(ST_GeomFromText('POLYGON((-75.17 39.95, ...etc...))'), 4326)"

    This function will then write two XLSX files:
        - total number of trips by station and year (one tab)
        - station-level numbers for inbound, outbound, and internal trips,
          broken out by year and month (one tab per station)
    """

    station_ids = _get_station_ids_from_wkt(
        study_area, include_inactive_stations=include_inactive_stations
    )

    print("Analyzing trips for station IDs:", station_ids)

    df = _mega_query(station_ids)

    # Inactive stations won't have a name or address, so we'll use their ID instead
    df["station_name"] = df["station_name"].fillna(df["station_id"].astype(int))

    if write_output_files:

        print(f"Writing files to {Path.cwd()}")

        # Write an excel file with a single table, annual ridership by station
        with pd.ExcelWriter("station_summary.xlsx") as writer:

            station_summary = df.pivot_table(
                index=["y"], columns=["station_name"], values="trips", aggfunc="sum"
            ).T
            station_summary.to_excel(writer, sheet_name="raw")

        # Write an excel file with one tab per station
        with pd.ExcelWriter("station_details.xlsx", engine="xlsxwriter") as writer:

            workbook = writer.book

            for station_id in df.station_id.unique():

                # Write the data table from pandas to excel
                sheet_name = f"trips_{int(station_id)}"
                filtered_df = df[df["station_id"] == station_id]
                filtered_df.pivot(
                    index=["y", "m"], columns=["trip_type"], values="trips"
                ).T.to_excel(writer, sheet_name=sheet_name)

                # Create the stacked column chart
                chart = workbook.add_chart({"type": "column", "subtype": "stacked"})
                for row_num, series_name in enumerate(["inbound", "internal", "outbound"], 4):
                    chart.add_series(
                        {
                            "name": series_name,
                            "values": f"={sheet_name}!B{row_num}:AT{row_num}",
                            "categories": f"={sheet_name}!B1:AT2",
                        }
                    )

                # Insert chart into excel tab
                worksheet = writer.sheets[sheet_name]
                worksheet.insert_chart("B8", chart)

    return df

from bikeshare_data import DEFAULT_PROJECT_BOUNDARY_SHP
from bikeshare_data.helpers import _import_polygon_shapefile, _execute_query, STUDY_AREA


_import_polygon_shapefile(DEFAULT_PROJECT_BOUNDARY_SHP)
_execute_query("CREATE INDEX ON study_area USING GIST(geom);")

# Filter to primary study area
q = f"""
    select start_station, end_station, st_makeline(start_geom, end_geom) as geom, count(*) as num_trips
    from trips_w_geom
    where st_within(start_geom, ({STUDY_AREA})) and not st_within(end_geom, ({STUDY_AREA}))
    and start_station != end_station
    group by start_geom, end_geom
    order by count(*) desc
"""

q = [
    # Create a table with trip records that have start and end geoms...
    # ... since not all of them have usable lat/lon on both trip ends
    """
            DROP TABLE IF EXISTS trips_w_geom;

            CREATE TABLE trips_w_geom AS
                SELECT *
                FROM trips
                WHERE start_geom IS NOT NULL
                    AND end_geom IS NOT NULL
        """,
    # Add a column to hold 'inbound', 'outbound' or 'roundtrip'
    """
            ALTER TABLE trips_w_geom
            ADD COLUMN trip_direction TEXT;

            UPDATE trips_w_geom
            SET 
        """,
]
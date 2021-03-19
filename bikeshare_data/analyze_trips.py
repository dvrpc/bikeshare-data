from bikeshare_data import STUDY_AREA, DEFAULT_DATA_FOLDER
from bikeshare_data.helpers import _get_query_result, _get_gdf


# Get a list of station IDs within study area
query = f"""
    SELECT id FROM station_shapes
	WHERE st_within(geom, ({STUDY_AREA}))
"""

sa_ids = _get_query_result(query)
sa_ids = str(tuple([x[0] for x in sa_ids]))

print(sa_ids)


# Build the big query for trips into and out of the study area
big_query = f"""
with trips_from as (
	select
        end_station, count(*) as from_sa
	from
        trips
	where
        start_station in {sa_ids}
	and
        end_station not in {sa_ids}
	group by
        end_station
),
trips_to as (
	select
        start_station, count(*) as to_sa
	from
        trips
	where
        start_station not in {sa_ids}
	and
        end_station in {sa_ids}
	group by
        start_station
)
select
    s.id,
    s.geom,
    f.from_sa,
    t.to_sa
from
    station_shapes s
left join
    trips_from f on s.id = f.end_station
left join
    trips_to t on s.id = t.start_station
"""

# Trips that start AND end within the study area
internal_desire_lines = f"""
WITH raw AS (
	SELECT
        start_station, end_station, count(*)
	FROM
        trips
    WHERE
        start_station IN {sa_ids}
    AND
        end_station IN {sa_ids}
	AND
        start_station != end_station
	GROUP BY
        start_station, end_station
)
SELECT
    raw.*, 
    ST_MakeLine(s.geom, e.geom) as geom
FROM
    raw
LEFT JOIN
    station_shapes s ON s.id = start_station
LEFT JOIN
    station_shapes e ON e.id = end_station
"""

internal_roundtrip_points = f"""
WITH raw AS (
	SELECT
        start_station, end_station, count(*)
	FROM
        trips
    WHERE
        start_station IN {sa_ids}
    AND
        end_station IN {sa_ids}
	AND
        start_station = end_station
	GROUP BY
        start_station, end_station
)
SELECT
    raw.*, s.geom as geom
FROM
    raw
LEFT JOIN
    station_shapes s ON s.id = start_station
"""

queries_to_save = [
    ("external_trips", big_query),
    ("internal_oneway", internal_desire_lines),
    ("internal_roundtrip", internal_roundtrip_points),
]
for shp_name, query in queries_to_save:
    gdf = _get_gdf(query)
    gdf.to_file(DEFAULT_DATA_FOLDER / shp_name)

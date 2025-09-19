from http import HTTPStatus

import pytest
import requests


WGS84_COORDINATES = [
    {"lon": -49.3124416, "lat": -25.4025905},
    {"lon": -46.634971, "lat": -23.559798},
    {"lon": 17.70188, "lat": 59.3258414},
    {"lon": 45.021838, "lat": 53.200386},
]


@pytest.mark.parametrize(
    'coordinates,elevation_m,start_time,end_time,maximum_sun_elevation', 
    [
        (WGS84_COORDINATES[0], 961, '2023-10-01T00:00:00Z', '2023-10-01T23:59:59Z', 67.85),
        (WGS84_COORDINATES[1], 776, '2024-01-01T00:00:00Z', '2024-01-01T23:59:59Z', 89.45),
        (WGS84_COORDINATES[2], 9, '2024-01-01T00:00:00Z', '2024-01-31T23:59:59Z', 13.28),
        (WGS84_COORDINATES[3], 142, '2024-01-01T00:00:00Z', '2024-12-31T23:59:59Z', 60.24),
    ],
)
def test_maximum_sun_elevation(
    coordinates, elevation_m, start_time, end_time, maximum_sun_elevation
):
    url = 'http://localhost:8000/maximum_sun_elevation'
    response = requests.post(url, json={
        'coordinates': coordinates,
        'elevation_m': elevation_m,
        'start_time': start_time,
        'end_time': end_time,
    })
    
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['maximum_sun_elevation'] == pytest.approx(maximum_sun_elevation, rel=0.1)
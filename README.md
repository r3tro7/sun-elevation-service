# Sun Elevation Microservice

Compute the maximum (apparent) sun elevation angle over a given UTC time range for WGS84 coordinates and observer elevation.

## API

`POST /maximum_sun_elevation`

Request body:
```
{
  "coordinates": {"lon": 17.70188, "lat": 59.3258414},
  "elevation_m": 25,
  "start_time": "2025-06-01T00:00:00Z",
  "end_time": "2025-06-01T23:59:59Z"
}
```

Response:
```
{ "maximum_sun_elevation": 51.234 }
```

- Times must be ISO-8601; if no timezone is given, UTC is assumed.
- Elevation uses a simple pressure-based refraction correction so apparent elevation is returned.

## Local Run

```
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Run the provided pytest integration test in another terminal:

```
pytest -q /mnt/data/integration_test.py
```

## Docker

```
docker build -t sun-elevation-service .
docker run --rm -p 8000:8000 sun-elevation-service
```

## Implementation Notes

- Pure-Python NOAA solar position math — no external ephemeris downloads required.
- Samples the time range at 1-minute resolution (adaptive for long ranges).
- Returns the **apparent** elevation (includes standard atmospheric refraction; scales with elevation via pressure model).
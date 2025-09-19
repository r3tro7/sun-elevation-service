# Sun Elevation Microservice

Bootstrap repo. Next steps will add a FastAPI service that computes
maximum sun elevation over a time range.

## Dev
```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## API
POST /maximum_sun_elevation

Example:
{
  "coordinates": {"lon": 17.70188, "lat": 59.3258414},
  "elevation_m": 25,
  "start_time": "2025-06-01T00:00:00Z",
  "end_time": "2025-06-01T23:59:59Z"
}

The service returns **apparent** sun elevation (includes standard refraction).

## Docker
docker build -t sun-elevation-service .
docker run --rm -p 8000:8000 sun-elevation-service

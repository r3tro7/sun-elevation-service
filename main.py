from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime, timedelta, timezone

from solar import solar_elevation


app = FastAPI(title="Sun Elevation Service")


class Coordinates(BaseModel):
    lon: float = Field(..., description="Longitude in degrees (WGS84, east positive)")
    lat: float = Field(..., description="Latitude in degrees (WGS84, north positive)")


class RequestModel(BaseModel):
    coordinates: Coordinates
    elevation_m: float
    start_time: str  # ISO-8601; if tz missing, assumed UTC
    end_time: str    # ISO-8601; if tz missing, assumed UTC


class ResponseModel(BaseModel):
    maximum_sun_elevation: float


def parse_time(s: str) -> datetime:
    """
    Accept ISO-8601 strings like '2025-06-01T00:00:00Z' or with offsets.
    Normalize to timezone-aware UTC datetimes.
    """
    if s.endswith("Z"):
        return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc)
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/maximum_sun_elevation", response_model=ResponseModel)
def maximum_sun_elevation(req: RequestModel):
    # Parse and validate times
    try:
        start = parse_time(req.start_time)
        end = parse_time(req.end_time)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid time format: {e}")

    if end <= start:
        raise HTTPException(status_code=400, detail="end_time must be after start_time")

    # Sample across the time range. Use 1-minute steps up to a cap for long windows.
    max_steps = 48 * 60  # ~2 days at 1-minute resolution
    total_minutes = int((end - start).total_seconds() // 60)
    step_minutes = 1 if total_minutes <= max_steps else max(1, total_minutes // max_steps)

    t = start
    max_elev = -90.0
    while t <= end:
        elev = solar_elevation(req.coordinates.lat, req.coordinates.lon, req.elevation_m, t)
        if elev > max_elev:
            max_elev = elev
        t += timedelta(minutes=step_minutes)

    return ResponseModel(maximum_sun_elevation=round(max_elev, 6))

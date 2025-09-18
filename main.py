from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict
from datetime import datetime, timedelta, timezone

from solar import solar_elevation

app = FastAPI(title="Sun Elevation Service")

class Coordinates(BaseModel):
    lon: float = Field(..., description="Longitude (WGS84)")
    lat: float = Field(..., description="Latitude (WGS84)")

class RequestModel(BaseModel):
    coordinates: Coordinates
    elevation_m: float
    start_time: str
    end_time: str

class ResponseModel(BaseModel):
    maximum_sun_elevation: float

def parse_time(s: str) -> datetime:
    if s.endswith('Z'):
        return datetime.fromisoformat(s.replace('Z', '+00:00')).astimezone(timezone.utc)
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

@app.post("/maximum_sun_elevation", response_model=ResponseModel)
def maximum_sun_elevation(req: RequestModel):
    try:
        start = parse_time(req.start_time)
        end = parse_time(req.end_time)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid time format: {e}")
    if end <= start:
        raise HTTPException(status_code=400, detail="end_time must be after start_time")

    max_steps = 48 * 60  # 2 days at 1-min steps
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

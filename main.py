from fastapi import FastAPI

app = FastAPI(title="Sun Elevation Service")

@app.get("/health")
def health():
    return {"status": "ok"}

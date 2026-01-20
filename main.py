from fastapi import FastAPI

app = FastAPI(title="Korvex Dashboard API")

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "korvex-dashboard-backend"
    }

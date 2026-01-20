import os
import requests
from datetime import datetime, timedelta

from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import RedirectResponse
from jose import jwt

# ================= CONFIG =================

DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
DISCORD_REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI")

JWT_SECRET = os.getenv("JWT_SECRET", "CHANGE_ME_NOW")
JWT_ALGORITHM = "HS256"

DISCORD_API_BASE = "https://discord.com/api"

# ================= APP =================

app = FastAPI(title="Korvex Dashboard API")

# ================= HELPERS =================

def create_jwt(user_id: int):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=12)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_jwt(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload["user_id"]
    except Exception:
        return None

# ================= ROUTES =================

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "korvex-dashboard-backend"
    }

# ---------- Discord OAuth ----------

@app.get("/auth/discord")
async def discord_login():
    url = (
        f"{DISCORD_API_BASE}/oauth2/authorize"
        f"?client_id={DISCORD_CLIENT_ID}"
        f"&redirect_uri={DISCORD_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=identify%20guilds"
    )
    return RedirectResponse(url)


@app.get("/auth/discord/callback")
async def discord_callback(code: str):
    token_response = requests.post(
        f"{DISCORD_API_BASE}/oauth2/token",
        data={
            "client_id": DISCORD_CLIENT_ID,
            "client_secret": DISCORD_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": DISCORD_REDIRECT_URI,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    if token_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get access token")

    access_token = token_response.json()["access_token"]

    user_response = requests.get(
        f"{DISCORD_API_BASE}/users/@me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    if user_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch user")

    user = user_response.json()
    jwt_token = create_jwt(int(user["id"]))

    return {
        "login": "success",
        "token": jwt_token,
        "user": user
    }

# ---------- Protected Route ----------

@app.get("/me")
async def get_me(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")

    token = authorization.replace("Bearer ", "")
    user_id = verify_jwt(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {"user_id": user_id}

# ---------- Health ----------

@app.get("/health")
async def health():
    return {"ok": True}    user_id = verify_jwt(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {"user_id": user_id}


@app.get("/health")
async def health():
    return {"ok": True}

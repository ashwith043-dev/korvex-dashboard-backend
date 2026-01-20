import os
import httpx
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI(title="Korvex Dashboard API")

DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
DISCORD_REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI")

DISCORD_API = "https://discord.com/api"


@app.get("/")
async def root():
    return {"status": "online", "service": "korvex-dashboard-backend"}


@app.get("/auth/discord")
async def discord_login():
    url = (
        f"{DISCORD_API}/oauth2/authorize"
        f"?client_id={DISCORD_CLIENT_ID}"
        f"&redirect_uri={DISCORD_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=identify guilds"
    )
    return RedirectResponse(url)


@app.get("/auth/discord/callback")
async def discord_callback(code: str):
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            f"{DISCORD_API}/oauth2/token",
            data={
                "client_id": DISCORD_CLIENT_ID,
                "client_secret": DISCORD_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": DISCORD_REDIRECT_URI,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        token_json = token_response.json()
        access_token = token_json["access_token"]

        user_response = await client.get(
            f"{DISCORD_API}/users/@me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    return {
        "login": "success",
        "user": user_response.json()
    }

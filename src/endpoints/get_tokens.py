from fastapi import APIRouter, Request
from src.utils.logger import configure_logging
import base64
from dotenv import load_dotenv
import httpx
import os

# Set up custom logger for error logging
log = configure_logging()

load_dotenv()

router = APIRouter()

@router.get("/get_tokens")
async def get_tokens(request: Request):
    query_params = request.query_params

    credentials = f"{os.getenv('CLIENT_ID')}:{os.getenv('CLIENT_SECRET')}"

    # Encode the concatenated string as bytes and then as base64
    base64_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

    data = {
        "grant_type": "authorization_code",
        "code": query_params.get('code'),
        "redirect_uri": 'http://localhost:9090/redirect',
    }

    headers = {
        "Authorization": f"Basic {base64_credentials}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    base_url = "https://accounts.spotify.com/api/token"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(base_url, data=data, headers=headers)
    except Exception as e:
        # Log the error message using the custom logger
        error_message = e
        log.error(error_message)
        return {"error": error_message}
from fastapi import APIRouter, Request
from src.utils.logger import configure_logging
import base64
from dotenv import load_dotenv
import httpx
import os
from src.utils.utils import refresh_tokens, retrieve_tokens, store_tokens

# Set up custom logger for error logging
log = configure_logging()

load_dotenv()

router = APIRouter()

@router.get("/authorize")
async def authorize(request: Request):
    query_params = request.query_params

    credentials = f"{os.getenv('CLIENT_ID')}:{os.getenv('CLIENT_SECRET')}"

    # Encode the concatenated string as bytes and then as base64
    base64_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

    body = {
        "grant_type": "authorization_code",
        "code": query_params.get('code'),
        "redirect_uri": 'https://kafrmcd72u.loclx.io/redirect',
    }

    headers = {
        "Authorization": f"Basic {base64_credentials}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    base_url = "https://accounts.spotify.com/api/token"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(base_url, data=body, headers=headers)
        data = response.json()
        return await store_tokens(data['access_token'], data['refresh_token'])
    except Exception as e:
        # Log the error message using the custom logger
        error_message = e
        log.error(error_message)
        return {"error": error_message}
    
@router.put("/authorize")
async def authorize(request: Request):
    query_params = request.query_params

    user_id = query_params['user_id']
    email = query_params['email']

    refresh_token = retrieve_tokens(user_id, email)["refresh_token"]

    credentials = f"{os.getenv('CLIENT_ID')}:{os.getenv('CLIENT_SECRET')}"

    # Encode the concatenated string as bytes and then as base64
    base64_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

    body = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    headers = {
        "Authorization": f"Basic {base64_credentials}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    base_url = "https://accounts.spotify.com/api/token"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(base_url, data=body, headers=headers)
        data = response.json()
        await refresh_tokens(user_id, email, data['access_token'], refresh_token)
    except Exception as e:
        # Log the error message using the custom logger
        error_message = e
        log.error(error_message)
        return {"error": error_message}
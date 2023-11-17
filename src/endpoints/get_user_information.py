from fastapi import APIRouter, Request
from src.utils.logger import configure_logging
from dotenv import load_dotenv
import httpx
from src.utils.utils import retrieve_tokens

# Set up custom logger for error logging
log = configure_logging()

load_dotenv()

router = APIRouter()

@router.get("/get_user_information")
async def get_user_information(request: Request):
    query_params = request.query_params

    user_id = query_params['user_id']
    email = query_params['email']

    tokens = retrieve_tokens(user_id, email)

    access_token = tokens["access_token"]

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    base_url = f"https://api.spotify.com/v1/users/{user_id}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(base_url, headers=headers)
        data = response.json()
        images = data["images"]
        if(len(images) != 0):
            return {"url": data["images"][0]["url"]}
        return {"url": ""}
    except Exception as e:
        # Log the error message using the custom logger
        error_message = e
        log.error(error_message)
        return {"error": error_message}
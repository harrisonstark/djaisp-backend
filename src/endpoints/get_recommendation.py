from fastapi import APIRouter, Request
from src.utils.logger import configure_logging
from src.utils.utils import add_query_params_to_url, get_user_info, retrieve_tokens
import httpx

# Set up custom logger for error logging
log = configure_logging()

router = APIRouter()

@router.get("/get_recommendation")
async def get_recommendation(request: Request):
    # TODO if tokens are expired then call a refresh and continue
    query_params = request.query_params

    user_id = query_params['user_id']
    email = query_params['email']

    access_token = retrieve_tokens(user_id, email)["access_token"]

    new_query_params = {}

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    # Base URL
    # Convert JSON data to query parameters
    base_url = add_query_params_to_url("https://api.spotify.com/v1/recommendations", new_query_params)

    # hardcode from example
    base_url = 'https://api.spotify.com/v1/recommendations?limit=10&seed_artists=6sFIWsNpZYqfjUpaCgueju&target_energy=.95&target_valence=.95'

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(base_url, headers=headers)
        data = response.json()
        return data
    except Exception as e:
        # Log the error message using the custom logger
        error_message = e
        log.error(error_message)
        return {"error": error_message}
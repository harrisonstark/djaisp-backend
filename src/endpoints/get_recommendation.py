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

    keys_to_exclude = ['user_id', 'email']

    new_query_params = {key: value for key, value in query_params.items() if key not in keys_to_exclude}

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    # Base URL
    # Convert JSON data to query parameters
    base_url = add_query_params_to_url("https://api.spotify.com/v1/recommendations", new_query_params)
    log.error(base_url)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(base_url, headers=headers)
        data = response.json()
        return [track["uri"] for track in data["tracks"]]
    except Exception as e:
        # Log the error message using the custom logger
        error_message = e
        log.error(error_message)
        return {"error": error_message}
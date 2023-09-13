from fastapi import APIRouter, Request
from src.utils.logger import configure_logging
from src.utils.utils import add_query_params_to_url
import httpx

# Set up custom logger for error logging
log = configure_logging()

router = APIRouter()

# TODO
@router.get("/get_recommendations")
async def get_recommendations(request: Request):
    # TODO if tokens are expired then call a refresh and continue
    query_params = request.query_params

    # Base URL
    base_url = "https://api.spotify.com/v1/recommendations"

    # Convert JSON data to query parameters
    query_params = add_query_params_to_url(base_url, query_params)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(query_params)
        data = response.json()
        return data
    except Exception as e:
        # Log the error message using the custom logger
        error_message = e
        log.error(error_message)
        return {"error": error_message}
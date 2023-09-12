from fastapi import APIRouter, Request
from logger import configure_logging
from utils import add_query_params_to_url
import httpx

# Set up custom logger for error logging
log = configure_logging()

router = APIRouter()

@router.get("/get_recommendations")
async def get_recommendations(request: Request):
    # Get JSON data from the request body (assuming it's a JSON request)
    try:
        json_data = await request.json()
    except ValueError:
        json_data = {}  # Set an empty dictionary if the request body is not JSON or empty

    # Base URL
    base_url = "https://api.spotify.com/v1/recommendations"

    # Convert JSON data to query parameters
    query_params = add_query_params_to_url(base_url, json_data)

    async with httpx.AsyncClient() as client:
        response = await client.get(query_params)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        # Log the error message using the custom logger
        error_message = "Request failed"
        log.error(error_message)
        return {"error": error_message}
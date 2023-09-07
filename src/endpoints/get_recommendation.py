from logger import configure_logging
from fastapi import APIRouter
import httpx

# Set up custom logger for error logging
log = configure_logging()

router = APIRouter()

@router.get("/get_recommendation")
async def get_recommendation():
    url = "https://api.example.com/data"  # Replace with the API endpoint you want to request

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        # Log the error message using the custom logger
        error_message = "Request failed"
        log.error(error_message)
        return {"error": error_message}
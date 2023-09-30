from fastapi import APIRouter, Request
from src.utils.logger import configure_logging
from src.utils.utils import add_query_params_to_url, get_user_info, retrieve_tokens
import urllib.parse
import httpx
import numpy as np
import json

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

    message = query_params.get('message', None)

    base_url = "https://api.spotify.com/v1/recommendations?limit=5"

    values = ["acousticness", "danceability", "energy", "instrumentalness", "liveness", "speechiness", "valence"]

    if(message):
        # TODO: seed_genres = chatgpt response, add query params seed_genres
        seed_genres = {"seed_genres": "indie-pop"}
        base_url = add_query_params_to_url(base_url, seed_genres)
        base_url = add_query_params_to_url(base_url, {"target_" + str(value): 0.5 for value in values})
    else:
        track_list = query_params['track_list']
        log.error(track_list)
        track_list = urllib.parse.unquote(track_list)
        log.error(track_list)
        track_list = json.loads(track_list)
        # Extract values for calculation
        attribute_values = {
            attribute: [v[attribute] for v in track_list.values()] for attribute in track_list["0"].keys() if attribute != "time_listened"
        }
        
        output_values = {"target_" + attribute: np.mean(0.5 + values * np.square([v["time_listened"] for v in track_list.values()]) - 0.5 * np.square([v["time_listened"] for v in track_list.values()]))
               for attribute, values in attribute_values.items()}
        seed_genres = query_params["seed_genres"]
        seed_genres = urllib.parse.unquote(seed_genres)
        seed_genres = {"seed_genres": seed_genres}
        base_url = add_query_params_to_url(base_url, seed_genres)
        base_url = add_query_params_to_url(base_url, output_values)
        log.error(output_values)
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(base_url, headers=headers)
        data = response.json()
        return {"songs": [track["uri"] for track in data["tracks"]], "seed_genres": seed_genres["seed_genres"]}
    except Exception as e:
        # Log the error message using the custom logger
        error_message = e
        log.error(error_message)
        return {"error": error_message}
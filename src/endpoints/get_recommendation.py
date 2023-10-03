import random
from fastapi import APIRouter, Request
from src.utils.logger import configure_logging
from src.utils.utils import add_query_params_to_url, get_seed_genres, retrieve_tokens
import urllib.parse
from datetime import datetime
import httpx
import numpy as np
import json

# Set up custom logger for error logging
log = configure_logging()

router = APIRouter()

@router.get("/get_recommendation")
async def get_recommendation(request: Request):
    query_params = request.query_params

    user_id = query_params['user_id']
    email = query_params['email']

    tokens = retrieve_tokens(user_id, email)

    #if(tokens["expire_time"] > datetime.now()):
        # TODO call a refresh and continue
        #refresh_tokens(tokens["user_id"], tokens["email"], tokens["access_token"], tokens["refresh_token"])

    access_token = tokens["access_token"]

    message = query_params.get('message', None)

    base_url = "https://api.spotify.com/v1/recommendations?limit=100"

    values = ["danceability", "energy", "instrumentalness", "speechiness", "valence"]

    if(message):
        message = urllib.parse.unquote(message)
        output_genres = await get_seed_genres(message)
        output_genres = json.loads(output_genres)
        seed_genres = ','.join(output_genres["genres"])
        base_url = add_query_params_to_url(base_url, {"seed_genres": seed_genres})
        base_url = add_query_params_to_url(base_url, {"target_" + str(value): random.uniform(0.1, 0.9) for value in values})
    else:
        track_list = query_params['track_list']
        track_list = urllib.parse.unquote(track_list)
        track_list = json.loads(track_list)

        # Extract "thumbs" values
        thumbs_values = [v["thumbs"] for v in track_list.values()]

        # Create arrays for "thumbs" equal to "up", "down", and ""
        up_array = [v for v, thumbs in zip(track_list.values(), thumbs_values) if thumbs == "up"]
        down_array = [v for v, thumbs in zip(track_list.values(), thumbs_values) if thumbs == "down"]
        empty_array = [v for v, thumbs in zip(track_list.values(), thumbs_values) if thumbs == ""]

        modified_down_array = [{attribute: 1 - value if attribute != "thumbs" else value for attribute, value in entry.items()} for entry in down_array]

        new_track_list_np = np.concatenate([up_array, up_array, modified_down_array, empty_array])

        # Extract values for calculation
        attribute_values = {
            attribute: [v[attribute] for v in new_track_list_np] for attribute in track_list["0"].keys() if attribute != "time_listened" and attribute != "thumbs"
        }
        
        output_values = {"target_" + attribute: np.mean(0.5 + values * np.square([track[attribute] for track in new_track_list_np]) - 
            0.5 * np.square([track[attribute] for track in new_track_list_np]))
            for attribute, values in attribute_values.items()}
        
        seed_genres = query_params["seed_genres"]
        seed_genres = urllib.parse.unquote(seed_genres)
        base_url = add_query_params_to_url(base_url, {"seed_genres": seed_genres})
        base_url = add_query_params_to_url(base_url, output_values)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(base_url, headers=headers)
        data = response.json()
        track_uris = [track["uri"] for track in data["tracks"]]
        random_track_indices = np.random.choice(len(track_uris), size=5, replace=False)
        selected_tracks = [track_uris[i] for i in random_track_indices]
        return {"songs": selected_tracks, "seed_genres": seed_genres}
    except Exception as e:
        # Log the error message using the custom logger
        error_message = e
        log.error(error_message)
        return {"error": error_message}
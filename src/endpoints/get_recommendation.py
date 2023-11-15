from math import floor
import random
from fastapi import APIRouter, Request
from src.utils.logger import configure_logging
from src.utils.utils import add_query_params_to_url, get_chatgpt_response, retrieve_tokens
import urllib.parse
import httpx
import numpy as np
import json
###
from emotion import build_model, VALENCE_MAP, AROUSAL_MAP, MODEL_CONFIG, LABELS
import tensorflow as tf
from layers import base_layers, projection_layers
from models import prado
###

# Set up custom logger for error logging
log = configure_logging()

router = APIRouter()

@router.get("/get_recommendation")
async def get_recommendation(request: Request):
    query_params = request.query_params

    user_id = query_params['user_id']
    email = query_params['email']

    tokens = retrieve_tokens(user_id, email)

    access_token = tokens["access_token"]

    message = query_params.get('message', None)

    base_url = "https://api.spotify.com/v1/recommendations?limit=100"

    values = ["danceability", "speechiness", "instrumentalness", "energy", "valence", "popularity"]

    ###
    model = build_model() #builds model
    model.load_weights('model/model_checkpoint') #loads weights from checkpoint
    ###
    
    if(message):
        seed_number = 1
        seed_count = 4
        prev_uri_list = []
        message = urllib.parse.unquote(message)
        output_genres = await get_chatgpt_response(message, "seed_genres")
        try:
            output_genres = json.loads(output_genres)
        except Exception as e:
            log.error("We had trouble parsing" + str(output_genres))
            return {"songs": {}, "seed_genres": {}, "seed_number": -1, "status": 400}
        seed_genres = ','.join(output_genres["genres"])
        base_url = add_query_params_to_url(base_url, {"seed_genres": seed_genres})
        
        ### should retrieve model output for values
        results = model.predict(x=[message]) #returns all probabilities for emotions
        labels = np.flip(np.argsort(results[0])) #sorts 

        label = LABELS[labels[0]]
        if label == 'neutral': #if neutral is the first option, get second-highest
            label = LABELS[labels[1]]
        valence = VALENCE_MAP[label] if VALENCE_MAP[label] else label
        arousal = AROUSAL_MAP[label] if AROUSAL_MAP[label] else label
        ###
        assigned_values = []
        assigned_values.append(("danceability",random.uniform(0.1,0.9)))
        assigned_values.append(("speechiness",random.uniform(0.1,0.9)))
        assigned_values.append(("instrumentalness",random.uniform(0.1,0.9)))
        #values from model
        assigned_values.append(("energy",valence))
        assigned_values.append(("valence",arousal))
        assigned_values.append(("popularity",random.uniform(10,90)))
        #modified base_url code
        base_url = add_query_params_to_url(base_url,{"target_" + str(entry[0]) : entry[1] for entry in assigned_values})
        #base_url = add_query_params_to_url(base_url, {"target_" + str(value): floor(random.uniform(10, 90)) if value == "popularity" else random.uniform(0.1, 0.9) for value in values})
        ###
    else:
        seed_number = int(query_params['seed_number'])
        seed_number = seed_number + 1
        seed_count = 16 if seed_number > 8 else seed_number * 2

        track_list = query_params['track_list']
        track_list = urllib.parse.unquote(track_list)
        try:
            track_list = json.loads(track_list)    
        except Exception as e:
            log.error("We had trouble parsing" + query_params['track_list'])
            return {"songs": {}, "seed_genres": {}, "seed_number": -1, "status": 400}

        prev_uri_list = [v["uri"] for v in track_list.values()]

        # Extract "thumbs" values
        thumbs_values = [v["thumbs"] for v in track_list.values()]

        # Create arrays for "thumbs" equal to "up", "down", and ""
        up_array = [v for v, thumbs in zip(track_list.values(), thumbs_values) if thumbs == "up"]
        down_array = [v for v, thumbs in zip(track_list.values(), thumbs_values) if thumbs == "down"]
        empty_array = [v for v, thumbs in zip(track_list.values(), thumbs_values) if thumbs == ""]

        modified_down_array = [{attribute: 100 - value if attribute == "popularity" else .5 if attribute == "time_listened" else 1 - value for attribute, value in entry.items() if attribute != "thumbs" and attribute != "uri"} for entry in down_array]

        new_track_list_np = np.concatenate([up_array, up_array, modified_down_array, empty_array])

        # Extract values for calculation
        attribute_values = {
            attribute: [v[attribute] for v in new_track_list_np] for attribute in track_list["0"].keys() if attribute != "thumbs" and attribute != "uri"
        }
        
        output_values = {"target_" + attribute: floor(np.mean(
            0.5 + (np.array(value) / 100) * np.square([track["time_listened"] for track in new_track_list_np]) -
            0.5 * np.square([track["time_listened"] for track in new_track_list_np])
        ) * 100) if attribute == "popularity" else
        np.mean(
            0.5 + value * np.square([track["time_listened"] for track in new_track_list_np]) -
            0.5 * np.square([track["time_listened"] for track in new_track_list_np])
        )
        for attribute, value in attribute_values.items() if attribute != "time_listened"}
        
        seed_genres = query_params["seed_genres"]
        seed_genres = urllib.parse.unquote(seed_genres)
        base_url = add_query_params_to_url(base_url, {"seed_genres": seed_genres})
        base_url = add_query_params_to_url(base_url, output_values)
    log.error(base_url)
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(base_url, headers=headers)
        data = response.json()
        track_uris = [track["uri"] for track in data["tracks"]]
        selected_tracks = []
        while len(selected_tracks) < seed_count:
            random_track_index = floor(np.random.choice(len(track_uris), size=1))
            selected_track = track_uris[random_track_index]
            if(selected_track not in selected_tracks and selected_track not in prev_uri_list):
                selected_tracks.append(selected_track)
        return {"songs": selected_tracks, "seed_genres": seed_genres, "seed_number": seed_number}
    except Exception as e:
        # Log the error message using the custom logger
        error_message = e
        log.error(error_message)
        return {"error": error_message}
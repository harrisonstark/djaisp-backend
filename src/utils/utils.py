from src.utils.database import Database
from datetime import datetime, timedelta
import httpx
from src.utils.logger import configure_logging
import urllib.parse
from dotenv import load_dotenv
import os

load_dotenv()

log = configure_logging()

def authenticate_request(auth):
    return auth == os.getenv('HSTOKEN')

def json_to_query_params(json_data):
    if not json_data:
        return ''

    query_params = urllib.parse.urlencode(json_data)
    return f'{query_params}'

def add_query_params_to_url(base_url, json_data):
    query_params = json_to_query_params(json_data)
    if('?' not in base_url):
        return f'{base_url}?{query_params}'
    return f'{base_url}&{query_params}'

def find_user(user_id, email):
    db = Database()
    user_info = {'user_id': user_id, 'email': email}
    return db.find_one_document(user_info) != None

async def get_user_info(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    base_url = 'https://api.spotify.com/v1/me'
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(base_url, headers=headers)
        data = response.json()
        return {'user_id': data['id'], 'email': data['email']}
    except Exception as e:
        # Log the error message using the custom logger
        error_message = e
        log.error(error_message)
        return {'error': error_message}

async def store_tokens(access_token, refresh_token = ''):
    db = Database()
    hour_from_now = datetime.now() + timedelta(hours=1)
    user_info = await get_user_info(access_token)
    user_id = user_info['user_id']
    email = user_info['email']
    # if user doesnt exist, otherwise you want to update
    document = {'user_id': user_id, 'email': email, 'access_token': access_token, 'expire_time': hour_from_now, 'refresh_token': refresh_token}
    if(find_user(user_id, email)):
        db.update_document(user_info, document)
    else:
        db.insert_document(document)
    return user_info

def retrieve_tokens(user_id, email):
    db = Database()
    document = {'user_id': user_id, 'email': email}
    return db.find_one_document(document)

async def refresh_tokens(user_id, email, access_token, refresh_token):
    db = Database()
    hour_from_now = datetime.now() + timedelta(hours=1)
    document = {'user_id': user_id, 'email': email, 'access_token': access_token, 'expire_time': hour_from_now, 'refresh_token': refresh_token}
    user_document = {'user_id': user_id, 'email': email}
    db.update_document(user_document, document)

async def get_chatgpt_response(message, type):
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    base_url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {OPENAI_API_KEY}'
    }
    body = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "system",
                "content": "respond in the JSON format: {'genres': [...]}, do not include any extraneous text. I want you to take in as input this user text and determine which 3, exactly 3, of the following genres would best fit their mood from this list of possible genres: {'genres': ['acoustic', 'afrobeat', 'alt-rock', 'alternative', 'ambient', 'anime', 'black-metal', 'bluegrass', 'blues', 'bossanova', 'brazil', 'breakbeat', 'british', 'cantopop', 'chicago-house', 'children', 'chill', 'classical', 'club', 'comedy', 'country', 'dance', 'dancehall', 'death-metal', 'deep-house', 'detroit-techno', 'disco', 'disney', 'drum-and-bass', 'dub', 'dubstep', 'edm', 'electro', 'electronic', 'emo', 'folk', 'forro', 'french', 'funk', 'garage', 'german', 'gospel', 'goth', 'grindcore', 'groove', 'grunge', 'guitar', 'happy', 'hard-rock', 'hardcore', 'hardstyle', 'heavy-metal', 'hip-hop', 'holidays', 'honky-tonk', 'house', 'idm', 'indian', 'indie', 'indie-pop', 'industrial', 'iranian', 'j-dance', 'j-idol', 'j-pop', 'j-rock', 'jazz', 'k-pop', 'kids', 'latin', 'latino', 'malay', 'mandopop', 'metal', 'metal-misc', 'metalcore', 'minimal-techno', 'movies', 'mpb', 'new-age', 'new-release', 'opera', 'pagode', 'party', 'philippines-opm', 'piano', 'pop', 'pop-film', 'post-dubstep', 'power-pop', 'progressive-house', 'psych-rock', 'punk', 'punk-rock', 'r-n-b', 'rainy-day', 'reggae', 'reggaeton', 'road-trip', 'rock', 'rock-n-roll', 'rockabilly', 'romance', 'sad', 'salsa', 'samba', 'sertanejo', 'show-tunes', 'singer-songwriter', 'ska', 'sleep', 'songwriter', 'soul', 'soundtracks', 'spanish', 'study', 'summer', 'swedish', 'synth-pop', 'tango', 'techno', 'trance', 'trip-hop', 'turkish', 'work-out', 'world-music']}"
            } if type == 'seed_genres' else
            {
                "role": "system",
                "content": "respond relatively informally in 1-2 sentences exactly, you are a DJ, " + ("setting" if type == "first_message" else "changing") + " the music to be associated with the user's mood, example: sad music for sad mood (DO NOT RESPOND TO THE USER WITH ANY ARTIST, ALBUM, OR SONG)"
            },
            {
                "role": "user", 
                "content": message
            }
        ],
        "response_format": {"type": "json_object" if type == 'seed_genres' else "text"}
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(base_url, json=body, headers=headers, timeout=60)
        data = response.json()
        return data['choices'][0]['message']['content']
    except httpx.HTTPStatusError as e:
        # Log the error message using the custom logger
        error_message = e.response.text
        status_code = e.response.status_code
        log.error(f"OpenAI API Error: {status_code} - {error_message}")
        return {'error': f'Error: Oops, I dropped my baton, please try again later. (Status Code: {status_code})', 'message': message}, status_code
    except Exception as e:
        # Log the error message using the custom logger
        error_message = e
        log.error(error_message)
        return {'error': 'Error: Oops, I dropped my baton, please try again later.', 'message': message}, 401
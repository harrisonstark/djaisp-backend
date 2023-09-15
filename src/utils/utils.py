from src.utils.database import Database
from datetime import datetime, timedelta
import httpx
import base64
from src.utils.logger import configure_logging
import urllib.parse
from dotenv import load_dotenv
import os

load_dotenv()

log = configure_logging()

def json_to_query_params(json_data):
    if not json_data:
        return ""

    query_params = urllib.parse.urlencode(json_data)
    return f"?{query_params}"

def add_query_params_to_url(base_url, json_data):
    query_params = json_to_query_params(json_data)
    return f"{base_url}{query_params}"

def find_user(user_id, email):
    db = Database()
    user_info = {'user_id': user_id, 'email': email}
    return db.find_one_document(user_info) != None

async def get_user_info(access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    base_url = "https://api.spotify.com/v1/me"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(base_url, headers=headers)
        data = response.json()
        return {'user_id': data['id'], 'email': data['email']}
    except Exception as e:
        # Log the error message using the custom logger
        error_message = e
        log.error(error_message)
        return {"error": error_message}

async def store_tokens(access_token, refresh_token = ""):
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

async def refresh_tokens(refresh_token):
    credentials = f"{os.getenv('CLIENT_ID')}:{os.getenv('CLIENT_SECRET')}"

    # Encode the concatenated string as bytes and then as base64
    base64_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

    body = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    headers = {
        "Authorization": f"Basic {base64_credentials}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    base_url = "https://accounts.spotify.com/api/token"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(base_url, data=body, headers=headers)
        data = response.json()
        await store_tokens(data['access_token'])
    except Exception as e:
        # Log the error message using the custom logger
        error_message = e
        log.error(error_message)
        return {"error": error_message}
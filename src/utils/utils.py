from src.utils.database import Database
from datetime import datetime, timedelta
import httpx
from src.utils.logger import configure_logging
import urllib.parse

log = configure_logging()

def json_to_query_params(json_data):
    if not json_data:
        return ""

    query_params = urllib.parse.urlencode(json_data)
    return f"?{query_params}"

def add_query_params_to_url(base_url, json_data):
    query_params = json_to_query_params(json_data)
    return f"{base_url}{query_params}"

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

async def store_tokens(access_token, refresh_token):
    db = Database()
    hour_from_now = datetime.now() + timedelta(hours=1)
    user_info = await get_user_info(access_token)
    user_id = user_info['user_id']
    email = user_info['email']
    # if user doesnt exist, otherwise you want to update
    document = {'user_id': user_id, 'email': email, 'access_token': access_token, 'expire_time': hour_from_now, 'refresh_token': refresh_token}
    return db.insert_document(document)

def retrieve_tokens(user_id, email):
    db = Database()
    document = {'user_id': user_id, 'email': email}
    return db.find_one_document(document)

def refresh_tokens(refresh_token):
    return
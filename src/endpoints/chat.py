import json
from fastapi import APIRouter, Request
from src.utils.logger import configure_logging
from src.utils.utils import get_chatgpt_response

# Set up custom logger for error logging
log = configure_logging()

router = APIRouter()

@router.post("/chat")
async def chat(request: Request):
    request_body = await request.body()

    # Decode the bytes to a UTF-8 string
    body_str = request_body.decode('utf-8')

    # Parse the JSON string
    json_data = json.loads(body_str)

    # Access the 'messages' key
    messages = json_data.get('messages', [])

    # Check if there are any messages
    if messages:
        # Get the most recent message
        last_message = messages[-1]

        message = last_message.get('content')

    return await get_chatgpt_response(message, "chat" if len(messages) > 2 else "first_message")
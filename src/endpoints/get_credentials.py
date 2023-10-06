from fastapi import APIRouter, Request
from src.utils.utils import retrieve_tokens

router = APIRouter()

@router.get("/get_credentials")
def get_credentials(request: Request):
    query_params = request.query_params
    user_id = query_params['user_id']
    email = query_params['email']
    tokens = retrieve_tokens(user_id, email)
    return {"access_token": tokens["access_token"], "expire_time": tokens["expire_time"]}
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.endpoints import authorize, chat, get_credentials, get_recommendation, get_user_information, healthcheck  # Import your endpoint modules here
from src.utils.model.emotion import predict_emotion
from tensorflow.saved_model import load
from src.utils.utils import authenticate_request

app = FastAPI()

# Configure CORS
origins = ["https://maistro.harrisonstark.net:9090", "http://maistro.harrisonstark.net:9090", "https://maistro.harrisonstark.net", "http://maistro.harrisonstark.net"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def check_authentication(request: Request, call_next):
    auth = request.headers.get('HSTOKEN')        
    if not authenticate_request(auth):
        return JSONResponse(status_code=401, content={'error': 'Unauthorized request'})
    return await call_next(request)

loaded_model = load('src/utils/model/bin.tf')

def predict_emotion_middleware(text):
    return predict_emotion(text, loaded_model)

@app.on_event("startup")
async def startup_event():
    app.state.predict_emotion = predict_emotion_middleware

# Include the routes from the imported endpoint modules
app.include_router(authorize.router)
app.include_router(chat.router)
app.include_router(get_credentials.router)
app.include_router(get_recommendation.router)
app.include_router(get_user_information.router)
app.include_router(healthcheck.router)

'''
# For future uses, example test cases could be added for endpoints, database, etc in separate file(s):
from fastapi.testclient import TestClient
from unittest.mock import patch

client = TestClient(app)

# Test for healthcheck endpoint
def test_healthcheck():
    response = client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    
# Retrieve_tokens from mock
def mock_retrieve_tokens(user_id, email):
    # Return mock tokens
    return {"access_token": "mocked_access_token", "expire_time": "mocked_expire_time"}

# Test for get_credentials endpoint
patch("src.utils.utls.retrieve_tokens", side_effect=mock_retrieve_tokens)
def test_get_credentials_success(mock_retrieve_tokens):
    response = client.get("/get_credentials?user_id=12345&email=example@example.com")
    assert response.status_code == 200
    assert response.json() == {
        "access_token": "mocked_access_token",
        "expire_time": "mocked_expire_time",
    }

# ... additional test cases
'''

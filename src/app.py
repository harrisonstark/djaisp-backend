from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.endpoints import authorize, chat, get_credentials, get_recommendation, get_user_information, healthcheck  # Import your endpoint modules here
from src.utils.model.emotion import predict_emotion
from tensorflow.saved_model import load

app = FastAPI()

# Configure CORS
origins = ["http://localhost:9090"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
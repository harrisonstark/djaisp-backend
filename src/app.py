from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.endpoints import get_recommendations, get_tokens, healthcheck  # Import your endpoint modules here

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

# Include the routes from the imported endpoint modules
app.include_router(get_recommendations.router)
app.include_router(get_tokens.router)
app.include_router(healthcheck.router)
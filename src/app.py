from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.endpoints import authorize, get_credentials, get_recommendation, healthcheck  # Import your endpoint modules here

app = FastAPI()

# Configure CORS
origins = ["https://localhost:9090", "https://jwcb4edygp.loclx.io"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routes from the imported endpoint modules
app.include_router(authorize.router)
app.include_router(get_credentials.router)
app.include_router(get_recommendation.router)
app.include_router(healthcheck.router)
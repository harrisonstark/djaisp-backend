from fastapi import FastAPI
from src.endpoints import get_recommendations, healthcheck  # Import your endpoint modules here

app = FastAPI()

# Include the routes from the imported endpoint modules
app.include_router(get_recommendations.router)
app.include_router(healthcheck.router)
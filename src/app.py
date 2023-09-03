from fastapi import FastAPI
from src.endpoints import healthcheck, endpoint_test_2  # Import your endpoint modules here

app = FastAPI()

# Include the routes from the imported endpoint modules
app.include_router(healthcheck.router)
app.include_router(endpoint_test_2.router)
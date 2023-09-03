from fastapi import APIRouter

router = APIRouter()

@router.get("/endpoint2")
async def get_endpoint2():
    return {"message": "Hello from endpoint2!"}
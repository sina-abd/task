from bson import ObjectId
from fastapi import HTTPException

def convert_object_id(data: dict) -> dict:
    """Helper to convert ObjectId to string."""
    data["_id"] = str(data["_id"])
    return data

def validate_object_id(id: str):
    """Validates if an ID is a valid ObjectId, raises an exception if not."""
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format.")
    return ObjectId(id)
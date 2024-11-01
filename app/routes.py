from fastapi import APIRouter, HTTPException, File, UploadFile, Depends
from fastapi.responses import JSONResponse
import pandas as pd
from database import collection
from models import UpdatePhoneRequest, MessageResponse, RecordResponse
from utils import convert_object_id, validate_object_id
from bson import ObjectId

router = APIRouter()

@router.post('/upload/', response_model=MessageResponse)
async def upload_file(file: UploadFile = File(...)) -> JSONResponse:
    """
    Endpoint to upload an .xlsx file, parse its contents, and insert the data into MongoDB.

    Args:
        file (UploadFile): The uploaded file, which must be an .xlsx file.

    Returns:
        JSONResponse: Success message with the count of records inserted.
    """
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="Only .xlsx files are supported.")

    try:
        df = pd.read_excel(file.file)
        data = df.to_dict(orient='records')
        if not data:
            raise HTTPException(status_code=400, detail="The file is empty.")
        
        result = collection.insert_many(data)
        return JSONResponse(content={'message': f'Successfully inserted {len(result.inserted_ids)} records.'}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.get('/read/', response_model=list[RecordResponse])
async def read_all_data():
    """
    Endpoint to retrieve all documents from the database.

    Returns:
        JSONResponse: List of all documents in the database, with `_id` fields converted to strings.
    
    Raises:
        HTTPException: If there is an error during data retrieval.
    """
     
    try:
        result = collection.find()
        data = [convert_object_id(document) for document in result]
        return JSONResponse(content=data, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading data: {str(e)}")

@router.get('/read/{id}/', response_model=RecordResponse)
async def read_data(id: str):
    """
    Endpoint to retrieve a single document by its ID.

    Args:
        id (str): The ID of the document to retrieve.

    Returns:
        JSONResponse: The requested document if found, with `_id` converted to a string.
    """
    validate_object_id(id)
    data = collection.find_one({'_id': ObjectId(id)})
    if data is None:
        raise HTTPException(status_code=404, detail="Record not found.")
    return JSONResponse(content=convert_object_id(data), status_code=200)

@router.patch('/read/{id}/', response_model=RecordResponse)
async def update_data(id: str, phone: UpdatePhoneRequest):
    """
    Endpoint to update the phone number of a document by its ID.

    Args:
        id (str): The ID of the document to update.
        phone (UpdatePhoneRequest): The new phone number to be updated.

    Returns:
        JSONResponse: The updated document's `_id` and phone number.
    """
    validate_object_id(id)
    result = collection.update_one({'_id': ObjectId(id)}, {'$set': {'phone': phone.phone_number}})
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Record not found or no changes made.")
    
    return JSONResponse(content={'_id': id, 'phone': phone.phone_number}, status_code=200)

@router.delete('/read/{id}/', response_model=MessageResponse)
async def delete_data(id: str):
    """
    Endpoint to delete a document by its ID.

    Args:
        id (str): The ID of the document to delete.

    Returns:
        JSONResponse: Success message confirming the deletion with the document's `_id`.
    """
    validate_object_id(id)
    result = collection.delete_one({'_id': ObjectId(id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Record not found.")
    
    return JSONResponse(content={'message': "Record deleted successfully", '_id': id}, status_code=200)
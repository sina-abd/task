import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi import UploadFile
from io import BytesIO
import pandas as pd
from bson import ObjectId
from .database import collection
from .routes import router

app = FastAPI()
app.include_router(router)

client = TestClient(app)

def create_sample_excel(data):
    df = pd.DataFrame(data)
    excel_file = BytesIO()
    df.to_excel(excel_file, index=False)
    excel_file.seek(0)
    return excel_file

sample_data = [
    {"name": "John Doe", "phone": "1234567890"},
    {"name": "Jane Doe", "phone": "0987654321"},
]

@pytest.fixture(autouse=True)
def clean_db():
    collection.delete_many({})

def test_upload_file_success():
    excel_file = create_sample_excel(sample_data)
    response = client.post("/upload/", files={"file": ("test.xlsx", excel_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    
    assert response.status_code == 200
    assert "Successfully inserted" in response.json()["message"]

def test_upload_file_invalid_extension():
    response = client.post("/upload/", files={"file": ("test.txt", BytesIO(b"test data"), "text/plain")})
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Only .xlsx files are supported."

def test_read_all_data_success():
    collection.insert_many(sample_data)
    
    response = client.get("/read/")
    assert response.status_code == 200
    assert len(response.json()) == len(sample_data)

def test_read_data_success():
    record_id = collection.insert_one(sample_data[0]).inserted_id
    
    response = client.get(f"/read/{record_id}/")
    assert response.status_code == 200
    assert response.json()["name"] == "John Doe"

def test_read_data_not_found():
    invalid_id = str(ObjectId()) 
    response = client.get(f"/read/{invalid_id}/")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Record not found."

def test_update_data_success():
    record_id = collection.insert_one(sample_data[0]).inserted_id
    new_phone = {"phone_number": "1112223333"}
    
    response = client.patch(f"/read/{record_id}/", json=new_phone)
    assert response.status_code == 200
    assert response.json()["phone"] == "1112223333"

def test_update_data_not_found():
    invalid_id = str(ObjectId())
    new_phone = {"phone_number": "1112223333"}
    
    response = client.patch(f"/read/{invalid_id}/", json=new_phone)
    assert response.status_code == 404
    assert response.json()["detail"] == "Record not found or no changes made."

def test_delete_data_success():
    record_id = collection.insert_one(sample_data[0]).inserted_id
    
    response = client.delete(f"/read/{record_id}/")
    assert response.status_code == 200
    assert response.json()["message"] == "Record deleted successfully"
    assert response.json()["_id"] == str(record_id)

def test_delete_data_not_found():
    invalid_id = str(ObjectId()) 
    
    response = client.delete(f"/read/{invalid_id}/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Record not found."

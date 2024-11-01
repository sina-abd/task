from pydantic import BaseModel

class UpdatePhoneRequest(BaseModel):
    phone_number: str

class MessageResponse(BaseModel):
    message: str
    _id: str | None = None

class RecordResponse(BaseModel):
    _id: str
    phone: str | None = None
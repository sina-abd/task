from fastapi import FastAPI
from .routes import router as api_router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.include_router(api_router)

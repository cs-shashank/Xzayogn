from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
from dotenv import load_dotenv

from scraper.buddy4study_scraper import Buddy4StudyScraper
from database.pinecone_manager import PineconeManager
from chatbot.scholarship_bot import ScholarshipBot
from config import (
    PINECONE_API_KEY,
    PINECONE_ENVIRONMENT,
    PINECONE_INDEX_NAME,
    BASE_URL
)


load_dotenv()

app = FastAPI(title="Scholarship Chatbot API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define your routes here...

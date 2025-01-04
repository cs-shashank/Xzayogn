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

# Pydantic models
class QueryRequest(BaseModel):
    question: str
    filters: Optional[Dict] = None

class ScrapingRequest(BaseModel):
    num_pages: int = 5

# Dependencies
def get_pinecone_manager():
    return PineconeManager(
        api_key=PINECONE_API_KEY,
        environment=PINECONE_ENVIRONMENT,
        index_name=PINECONE_INDEX_NAME,
        openai_api_key=os.getenv('OPENAI_API_KEY')
    )

def get_scraper():
    return Buddy4StudyScraper(BASE_URL)

def get_chatbot():
    return ScholarshipBot(os.getenv('OPENAI_API_KEY'))

# Routes
@app.post("/scrape")
async def scrape_scholarships(
    request: ScrapingRequest,
    scraper: Buddy4StudyScraper = Depends(get_scraper),
    db: PineconeManager = Depends(get_pinecone_manager)
):
    try:
        scholarships = scraper.scrape_scholarships(request.num_pages)
        if not scholarships:
            raise HTTPException(status_code=404, detail="No scholarships found")
        
        db.upsert_scholarships(scholarships)
        return {"message": f"Successfully scraped and stored {len(scholarships)} scholarships"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query_scholarships(
    request: QueryRequest,
    db: PineconeManager = Depends(get_pinecone_manager),
    chatbot: ScholarshipBot = Depends(get_chatbot)
):
    try:
        # Get relevant scholarships from Pinecone
        scholarships = db.query_scholarships(
            query=request.question,
            filters=request.filters
        )
        
        if not scholarships:
            return {
                "answer": "I couldn't find any scholarships matching your criteria. Please try a different query."
            }
        
        # Generate chatbot response
        response = await chatbot.get_response(
            question=request.question,
            scholarships=scholarships
        )
        
        return {
            "answer": response,
            "scholarships": scholarships
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
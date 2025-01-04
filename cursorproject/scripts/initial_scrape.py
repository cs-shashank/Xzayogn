import asyncio
import os
from dotenv import load_dotenv
from scraper.buddy4study_scraper import Buddy4StudyScraper
from database.pinecone_manager import PineconeManager
from config import (
    PINECONE_API_KEY,
    PINECONE_ENVIRONMENT,
    PINECONE_INDEX_NAME,
    BASE_URL
)

load_dotenv()

async def main():
    # Initialize components
    scraper = Buddy4StudyScraper(BASE_URL)
    db = PineconeManager(
        api_key=PINECONE_API_KEY,
        environment=PINECONE_ENVIRONMENT,
        index_name=PINECONE_INDEX_NAME,
        openai_api_key=os.getenv('OPENAI_API_KEY')
    )
    
    # Scrape scholarships
    print("Starting scholarship scraping...")
    scholarships = scraper.scrape_scholarships(num_pages=10)
    print(f"Scraped {len(scholarships)} scholarships")
    
    # Store in Pinecone
    print("Storing scholarships in Pinecone...")
    db.upsert_scholarships(scholarships)
    print("Done!")

if __name__ == "__main__":
    asyncio.run(main()) 
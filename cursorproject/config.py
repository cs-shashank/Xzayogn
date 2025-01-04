import os
from dotenv import load_dotenv

load_dotenv()

# Pinecone Configuration
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENVIRONMENT = os.getenv('PINECONE_ENVIRONMENT')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME')

# Scraping Configuration
BASE_URL = "https://www.buddy4study.com"
SCHOLARSHIPS_URL = f"{BASE_URL}/scholarships"

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000
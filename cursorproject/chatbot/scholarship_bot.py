from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from typing import List, Dict
import logging
import asyncio
from pydantic import BaseModel
from openai import OpenAI
# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScholarshipBot:
    def __init__(self, openai_api_key: str):
        # Initialize OpenAI model using ChatOpenAI from langchain
        self.llm = ChatOpenAI(
            temperature=0.7,
            model_name="gpt-3.5-turbo",
            openai_api_key=openai_api_key
        )
        
        # Create prompt using ChatPromptTemplate
        self.prompt = ChatPromptTemplate.from_template(
            """You are a helpful scholarship advisor. Using the following scholarship information, 
            answer the user's question accurately and concisely.

            Scholarship Information:
            {scholarship_info}

            User Question: {question}

            Please provide a helpful response that directly addresses the user's question.
            Include specific details about relevant scholarships, such as deadlines, award amounts, 
            and eligibility criteria. If the information is not available in the scholarship data, 
            please say so politely."""
        )
        
        # Initialize LLMChain with the model and the prompt
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def _format_scholarship_info(self, scholarships: List[Dict]) -> str:
        formatted_info = []
        for i, scholarship in enumerate(scholarships, 1):
            info = [
                f"\nScholarship #{i}:",
                f"Title: {scholarship['title']}",
                f"Award: {scholarship['award']}",
                f"Deadline: {scholarship['deadline']}",
                f"Eligibility: {', '.join(scholarship['eligibility'])}",
                f"Application Process: {', '.join(scholarship['application_process'])}",
                f"Documents Required: {', '.join(scholarship['documents_required'])}",
                f"Country: {scholarship['country']}",
                f"Education Level: {scholarship['education_level']}",
                f"URL: {scholarship['url']}"
            ]
            formatted_info.append("\n".join(info))
        return "\n".join(formatted_info)

    def respond_to_query(self, query: str, scholarships: List[Dict]) -> str:
        # Logic to respond to user queries
        return asyncio.run(self.get_response(query, scholarships))

    async def get_response(self, question: str, scholarships: List[Dict]) -> str:
        try:
            scholarship_info = self._format_scholarship_info(scholarships)
            logger.info(f"Formatted Scholarship Info: {scholarship_info}")
            logger.info(f"User Question: {question}")
            
            # Generate response using LLMChain
            response = await self.chain.arun(
                scholarship_info=scholarship_info,
                question=question
            )
            logger.info(f"Response from API: {response}")
            return response.strip()
        except Exception as e:
            logger.error(f"Error generating chatbot response: {e}")
            return "I apologize, but I'm having trouble processing your request at the moment. Please try again later."

# Example usage
if __name__ == "__main__":
    openai_api_key = "replace"  # Replace with your actual OpenAI API key
    bot = ScholarshipBot(openai_api_key)

    # Example scholarship data (replace with actual data)
    scholarships = [
        {
            "title": "Example Scholarship",
            "award": "$1000",
            "deadline": "2023-12-31",
            "eligibility": ["High School", "Undergraduate"],
            "application_process": ["Online Application"],
            "documents_required": ["Transcript", "Essay"],
            "country": "USA",
            "education_level": "Undergraduate",
            "url": "http://example.com"
        }
    ]

    # Chat loop to interact with the bot
    while True:
        user_input = input("You: ")
        response = bot.respond_to_query(user_input, scholarships)
        print(f"Bot: {response}")

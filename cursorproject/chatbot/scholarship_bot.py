from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from typing import List, Dict
import logging
import asyncio
import time
from scholarship_data import scholarships  # Use absolute import

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScholarshipBot:
    def __init__(self, openai_api_key: str = None):
        if openai_api_key:
            self.llm = ChatOpenAI(
                temperature=0.7,
                model_name="gpt-3.5-turbo",
                openai_api_key=openai_api_key
            )
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
            self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
        else:
            self.llm = None
            self.prompt = None

    def _format_scholarship_info(self, scholarships: List[Dict]) -> str:
        formatted_info = []
        for i, scholarship in enumerate(scholarships, 1):
            info = [
                f"\nScholarship #{i}:",
                f"Title: {scholarship.get('title', 'N/A')}",
                f"Award: {scholarship.get('award', 'N/A')}",
                f"Deadline: {scholarship.get('deadline', 'N/A')}",
                f"Eligibility: {', '.join(scholarship.get('eligibility', ['N/A']))}",
                f"Application Process: {', '.join(scholarship.get('application_process', ['N/A']))}",
                f"Documents Required: {', '.join(scholarship.get('documents_required', ['N/A']))}",
                f"Country: {scholarship.get('country', 'N/A')}",
                f"Education Level: {scholarship.get('education_level', 'N/A')}",
                f"URL: {scholarship.get('url', 'N/A')}"
            ]
            formatted_info.append("\n".join(info))
        return "\n".join(formatted_info)

    def respond_to_query(self, query: str, scholarships: List[Dict]) -> str:
        return asyncio.run(self.get_response(query, scholarships))

    async def get_response(self, question: str, scholarships: List[Dict]) -> str:
        """Generate a response based on the user's question and scholarship information."""
        scholarship_info = self._format_scholarship_info(scholarships)
        logger.info(f"Formatted Scholarship Info: {scholarship_info}")
        logger.info(f"User Question: {question}")

        if self.llm is None:
            return "No LLM initialized for mock responses."

        # Retry mechanism with exponential backoff
        for attempt in range(5):
            try:
                await asyncio.sleep(2)  # Initial delay before the request
                response = await self.chain.invoke(
                    {"scholarship_info": scholarship_info, "question": question}
                )
                return response.strip()
            except Exception as e:
                if "429" in str(e):
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Error generating chatbot response: {e}")
                    return "I apologize, but I'm having trouble processing your request at the moment. Please try again later."

if __name__ == "__main__":
    # Initialize the bot with your OpenAI API key
    openai_api_key ="skhdDSmCcecVqqAxScPycS4A"  # Replace with your actual OpenAI API key
    bot = ScholarshipBot(openai_api_key)

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting the chatbot. Goodbye!")
            break
        response = bot.respond_to_query(user_input, scholarships)
        print(f"Bot: {response}")

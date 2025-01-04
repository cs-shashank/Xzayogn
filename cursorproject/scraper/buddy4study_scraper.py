import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Buddy4StudyScraper:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def get_scholarship_links(self, page: int = 1) -> List[str]:
        try:
            url = f"{self.base_url}/scholarships/page/{page}"
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            scholarship_cards = soup.find_all('div', class_='scholarship-card')
            
            return [
                f"{self.base_url}{card.find('a')['href']}"
                for card in scholarship_cards
            ]
        except Exception as e:
            logger.error(f"Error fetching scholarship links: {e}")
            return []

    def scrape_scholarship_details(self, url: str) -> Dict:
        try:
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            return {
                'title': self._get_text(soup, 'h1', class_='scholarship-title'),
                'deadline': self._get_text(soup, 'div', class_='deadline-date'),
                'eligibility': self._get_eligibility(soup),
                'award': self._get_text(soup, 'div', class_='award-amount'),
                'description': self._get_text(soup, 'div', class_='description'),
                'application_process': self._get_application_process(soup),
                'documents_required': self._get_documents(soup),
                'url': url,
                'country': self._get_text(soup, 'div', class_='country'),
                'education_level': self._get_text(soup, 'div', class_='education-level'),
                'last_updated': self._get_text(soup, 'div', class_='last-updated')
            }
        except Exception as e:
            logger.error(f"Error scraping scholarship details: {e}")
            return {}

    def _get_text(self, soup: BeautifulSoup, tag: str, class_: str) -> str:
        element = soup.find(tag, class_=class_)
        return element.text.strip() if element else ""

    def _get_eligibility(self, soup: BeautifulSoup) -> List[str]:
        eligibility_div = soup.find('div', class_='eligibility-criteria')
        if not eligibility_div:
            return []
        
        criteria = eligibility_div.find_all('li')
        return [item.text.strip() for item in criteria]

    def _get_application_process(self, soup: BeautifulSoup) -> List[str]:
        process_div = soup.find('div', class_='application-process')
        if not process_div:
            return []
        steps = process_div.find_all('li')
        return [step.text.strip() for step in steps]

    def _get_documents(self, soup: BeautifulSoup) -> List[str]:
        docs_div = soup.find('div', class_='required-documents')
        if not docs_div:
            return []
        docs = docs_div.find_all('li')
        return [doc.text.strip() for doc in docs]

    def scrape_scholarships(self, num_pages: int = 5) -> List[Dict]:
        all_scholarships = []
        
        for page in range(1, num_pages + 1):
            logger.info(f"Scraping page {page}")
            links = self.get_scholarship_links(page)
            
            for link in links:
                scholarship = self.scrape_scholarship_details(link)
                if scholarship:
                    all_scholarships.append(scholarship)
                    
        return all_scholarships 
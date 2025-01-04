import requests
from bs4 import BeautifulSoup

def scrape_scholarships():
    url = "https://www.buddy4study.com/scholarships"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    scholarships = []
    for scholarship in soup.find_all('div', class_='scholarship-card'):
        title = scholarship.find('h3').text.strip()
        award = scholarship.find('span', class_='award-amount').text.strip()
        deadline = scholarship.find('span', class_='deadline').text.strip()
        eligibility = scholarship.find('span', class_='eligibility').text.strip().split(',')
        scholarships.append({
            "title": title,
            "award": award,
            "deadline": deadline,
            "eligibility": [e.strip() for e in eligibility],
            "application_process": ["Online Application"],  # Example
            "documents_required": ["Documents"],  # Example
            "country": "India",  # Example
            "education_level": "Undergraduate",  # Example
            "url": url
        })
    return scholarships
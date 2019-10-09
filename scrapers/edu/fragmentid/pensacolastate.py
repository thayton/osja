import re
import json
import logging
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin

def extract_text(soup):
    text = soup.get_text()
    text = ' '.join( text.split() )
    return text

class PensacolaStateJobScraper(object):
    def __init__(self):
        self.url = 'https://www.pensacolastate.edu/employment-full-time-positions/'
        self.params = {
            'page': 1,
        }

        FORMAT = "%(asctime)s [ %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
        logging.basicConfig(format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        
        self.session = requests.Session()
        
    def scrape_job_description(self, job):
        assert job['url'] is not None
        return job['description']
        
    def scrape_job_listings(self):
        jobs = []

        resp = self.session.get(self.url)
        soup = BeautifulSoup(resp.text, 'lxml')

        r = re.compile(r'^#(adjuct-jobs-\d+)$')
        
        for a in soup.find_all('a', href=r):
            m = re.search(r, a['href'])
            fragment_id = m.group(1)
            d = soup.find('div', id=fragment_id)
            
            job = {}
            job['title'] = a.text.strip()
            job['url'] = urljoin(self.url, a['href'])
            job['location'] = 'Pensacola, FL'
            job['description'] = extract_text(d)
            jobs.append(job)

        return jobs

    def scrape(self):
        jobs = self.scrape_job_listings()
        for j in jobs:
            self.scrape_job_description(j)

        print(json.dumps(jobs, indent=2))

if __name__ == '__main__':
    scraper = PensacolaStateJobScraper()
    scraper.scrape()
        

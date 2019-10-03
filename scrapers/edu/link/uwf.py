import json
import logging
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin

class UwfJobScraper(object):
    def __init__(self):
        self.url = 'https://jobs.uwf.edu/postings/search'
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

        resp = self.session.get(job['url'])
        soup = BeautifulSoup(resp.text, 'html.parser')

        d = soup.find('div', id='form_view')

        job['description'] = d.text.strip()
        
    def scrape_job_listings(self):
        jobs = []

        while True:
            resp = self.session.get(self.url, params=self.params)
            soup = BeautifulSoup(resp.text, 'html.parser')

            for a in soup.select('div#search_results div.job-title > h3 > a'):
                job = {}
                job['title'] = a.text.strip()
                job['url'] = urljoin(self.url, a['href'])
                job['location'] = 'Pensacola, FL'
                jobs.append(job)

            next_page = soup.select_one('a.next_page')
            if next_page is None:
                break

            self.params['page'] += 1

        return jobs

    def scrape(self):
        jobs = self.scrape_job_listings()
        for j in jobs:
            self.scrape_job_description(j)

        print(json.dumps(jobs, indent=2))

if __name__ == '__main__':
    scraper = UwfJobScraper()
    scraper.scrape()
        

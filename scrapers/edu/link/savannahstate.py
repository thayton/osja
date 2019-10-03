import json
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin

class SavannahStateJobScraper(object):
    def __init__(self):
        self.session = requests.Session()        
        self.url = 'https://jobs.savannahstate.edu/postings/search'
        self.params = {
            'commit': 'Search',
            'page': 1,
            'query_organizational_tier_3_id': 'any',
            'query_position_type_id': 1
        }

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
                job['location'] = 'Savannah, GA'
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
    scraper = SavannahStateJobScraper()
    scraper.scrape()
        

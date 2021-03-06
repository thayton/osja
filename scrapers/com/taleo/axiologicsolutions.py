import time
import json
import logging
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin

class RuralSourcingJobScraper(object):
    def __init__(self):
        self.url = 'https://chu.tbe.taleo.net/chu01/ats/careers/v2/searchResults'
        self.headers = {
            'X-Requested-With': 'XMLHttpRequest'
        }

        self.params = {
            'org': 'AXIOSOLU',
            'cws': 37,
            'next': None,
            'rowFrom': 0,
            'act': 'null',
            'sortColumn': 'null',
            'sortOrder': 'null',
            'currentTime': int(time.time())
        }
        
        self.session = requests.Session()

    def scrape_job_links(self):
        jobs = []

        while True:
            resp = self.session.get(self.url, headers=self.headers, params=self.params)
            soup = BeautifulSoup(resp.text, 'lxml')
            divs = soup.select('div.oracletaleocwsv2-accordion-head-info')
            
            for d in divs:
                a = d.h4.a

                job = {}
                job['title'] = a.text
                job['url'] = urljoin(self.url, a['href'])
                job['location'] = d.find_all('div')[-1].text
                jobs.append(job)

            if len(divs) == 0:
                break

            self.params['rowFrom'] += 10

        return jobs

    def scrape_job_description(self, job):
        assert job['url'] != None, 'Job URL must be set'

        resp = self.session.get(job['url'])
        soup = BeautifulSoup(resp.text, 'html.parser')

        d = soup.select('div.row')[1]

        # Remove <script> from description
        for s in d.find_all('script'):
            s.extract()

        job['description'] = str(d)
        
    def scrape(self):
        jobs = self.scrape_job_links()
        for j in jobs:
            self.scrape_job_description(j)

        print(json.dumps(jobs, indent=2))

if __name__ == '__main__':
    scraper = RuralSourcingJobScraper()
    scraper.scrape()
    

import time
import json
import logging
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin

class AlionScienceJobScraper(object):
    def __init__(self):
        self.url = 'https://jobs.alionscience.com/en-US/search'
        self.params = {
            'keywords': None,
            'location': None,
            'pagenumber': 1
        }

        FORMAT = "%(asctime)s [ %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
        logging.basicConfig(format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.session = requests.Session()

    def scrape_job_description(self, job):
        assert job.get('url') != None, 'Job URL is not set'

        resp = self.session.get(job['url'])
        soup = BeautifulSoup(resp.text, 'lxml')

        div = soup.select_one('div#jdp-job-description-section')
        job['description'] = div.text.strip()

        return job['description']

    def scrape_job_links(self):
        assert self.url != None, 'Jobs page URL is not set'
        
        jobs = []
        
        url = self.url
        css_sel = 'table#job-result-table > tbody > tr.job-result > td > a.job-result-title'
        
        while True:
            self.logger.info(f'Getting page {self.params["pagenumber"]}')
            
            resp = self.session.get(url, params=self.params)
            soup = BeautifulSoup(resp.text, 'lxml')
            
            for a in soup.select(css_sel):
                tr = a.find_parent('tr')
                d = tr.select_one('div.job-location-line')
                
                job = {}
                job['title'] = a.text.strip()
                job['location'] = d.text.strip()
                job['url'] = urljoin(self.url, a['href'])

                jobs.append(job)

            self.params['pagenumber'] += 1
            
            f = lambda t: t.name == 'a' and t.text.strip() == f"{self.params['pagenumber']}"

            next_page = soup.find(f)
            if next_page == None:
                break

        self.logger.info(f'Returning {len(jobs)} jobs')
        return jobs

    def scrape(self):
        jobs = self.scrape_job_links()

        for j in jobs:
            self.scrape_job_description(j)

        return jobs

if __name__ == '__main__':
    scraper = AlionScienceJobScraper()
    jobs = scraper.scrape()
    print(json.dumps(jobs, indent=2))
        

        

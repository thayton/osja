import json
import logging
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin

class UsmMaineJobScraper(object):
    def __init__(self):
        self.url = 'https://usm.hiretouch.com/view-all-jobs/default.cfm'
        self.params = {
            'per': 25,
            'start': 1
        }

        FORMAT = "%(asctime)s [ %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
        logging.basicConfig(format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        
        self.session = requests.Session()
        
    def scrape_job_description(self, job):
        assert job['url'] is not None

        resp = self.session.get(job['url'])
        soup = BeautifulSoup(resp.text, 'lxml')

        d = soup.find('div', id='element_jobdetails')

        for script in d.find_all('script'):
            script.extract()
        
        desc = [ t.split() for t in d.find_all(text=True) ]
        desc = [ ' '.join(l) for l in desc if len(l) > 0 ]
        
        job['description'] = ' '.join(desc)
        return job['description']

    def scrape_job_listings(self):
        jobs = []

        while True:
            resp = self.session.get(self.url, params=self.params)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            for a in soup.select('ul.jobs > li.job > h4 > a'):
                p = a.find_next('span', id='field_for_organization')
                
                job = {}
                job['title'] = a.text.strip()
                job['url'] = urljoin(self.url, a['href'])
                job['location'] = p.text.strip()
                jobs.append(job)

            next_page = soup.select_one('ul.pagination > li.pagination_next > a')
            if 'not_active' in next_page.attrs.get('class', []):
                break

            self.params['start'] = len(jobs) + 1

        return jobs

    def scrape(self):
        jobs = self.scrape_job_listings()
        for j in jobs:
            self.scrape_job_description(j)

        print(json.dumps(jobs, indent=2))

if __name__ == '__main__':
    scraper = UsmMaineJobScraper()
    scraper.scrape()
        

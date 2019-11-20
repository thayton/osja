import time
import json
import logging
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin

class MojaJobScraper(object):
    def __init__(self):
        self.url = 'https://moja.applicantstack.com/x/openings'

        FORMAT = "%(asctime)s [ %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
        logging.basicConfig(format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.session = requests.Session()

    def scrape_job_description(self, job):
        assert job.get('url') != None, 'Job URL is not set'

        resp = self.session.get(job['url'])
        soup = BeautifulSoup(resp.text, 'lxml')

        d = soup.select_one('div#ascontent')
        
        for script in d.find_all('script'):
            script.extract()

        desc = [ t.split() for t in d.find_all(text=True) ]
        desc = [ ' '.join(l) for l in desc if len(l) > 0 ]
        
        job['description'] = ' '.join(desc)
        return job['description']

    def scrape_job_links(self):
        assert self.url != None, 'Jobs page URL is not set'

        jobs = []
        
        resp = self.session.get(self.url)
        soup = BeautifulSoup(resp.text, 'lxml')

        for a in soup.select('table#data-table > tbody > tr > td > a'):
            tr = a.find_parent('tr')
            td = tr.find_all('td')
            
            job = {}
            job['title'] = a.text.strip()
            job['location'] = td[-1].text.strip()
            job['url'] = urljoin(self.url, a['href'])

            jobs.append(job)

        return jobs

    def scrape(self):
        jobs = self.scrape_job_links()

        for j in jobs:
            self.scrape_job_description(j)

        return jobs

if __name__ == '__main__':
    scraper = MojaJobScraper()
    jobs = scraper.scrape()
    print(json.dumps(jobs, indent=2))
        

        

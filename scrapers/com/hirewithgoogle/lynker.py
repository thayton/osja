import time
import json
import logging
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin

class LynkerJobScraper(object):
    def __init__(self):
        self.url = 'https://hire.withgoogle.com/public/jobs/lynkertechcom'

        FORMAT = "%(asctime)s [ %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
        logging.basicConfig(format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.session = requests.Session()

    def scrape_job_description(self, job):
        assert job.get('url') != None, 'Job URL is not set'

        resp = self.session.get(job['url'])
        soup = BeautifulSoup(resp.text, 'lxml')

        header = soup.select_one('div.bb-jobs-posting__header')
        content = soup.select_one('div.bb-jobs-posting__content')

        desc = ' '.join(header.find_all(text=True) + content.find_all(text=True))
        job['description'] = desc

        return job['description']

    def scrape_job_links(self):
        assert self.url != None, 'Jobs page URL is not set'

        jobs = []

        resp = self.session.get(self.url)
        soup = BeautifulSoup(resp.text, 'lxml')

        d = soup.select_one('div.bb-public-jobs-list__positions-container')

        for a in d.select('a.bb-public-jobs-list__item-link'):
            t = a.select_one('span.ptor-jobs-list__item-job-title')
            l = a.select_one('span.ptor-jobs-list__item-location')

            job = {}
            job['title'] = t.text.strip()
            job['location'] = l.text.strip()
            job['url'] = urljoin(self.url, a['href'])

            jobs.append(job)
            
        return jobs

    def scrape(self):
        jobs = self.scrape_job_links()

        for j in jobs:
            self.scrape_job_description(j)

        return jobs

if __name__ == '__main__':
    scraper = LynkerJobScraper()
    jobs = scraper.scrape()
    print(json.dumps(jobs, indent=2))
        

        

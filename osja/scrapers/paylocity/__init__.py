import re
import json
import logging
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin

class PaylocityJobScraper(object):
    def __init__(self):
        self.session = requests.Session()

        FORMAT = "%(asctime)s [ %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
        logging.basicConfig(format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        
    def scrape_job_description(self, job):
        assert job.get('url') != None, 'Job URL is not set'

        resp = self.session.get(job['url'])
        soup = BeautifulSoup(resp.text, 'lxml')
        
        script = soup.find('script', attrs={ 'type': 'application/ld+json' })
        
        data = json.loads(script.text)
        desc = BeautifulSoup(data['description'], 'lxml')
        
        job['description'] = desc.text.strip()
        return job['description']

    def scrape_job_links(self):
        assert self.url != None, 'Jobs page URL is not set'

        jobs = []
        jobs_base_url = '/Recruiting/Jobs/Details/%d'

        resp = self.session.get(self.url)
        r = re.compile(r'window\.pageData\s+=\s+({[^;]+);')        
        m = re.search(r, resp.text)
        data = json.loads(m.group(1))

        for j in data['Jobs']:
            job = {}
            job['url'] = urljoin(self.url, jobs_base_url % j['JobId'])
            job['title'] = j['JobTitle']
            job['location'] = j['JobLocation']['City'] + ', ' + j['JobLocation']['State']
            jobs.append(job)

        return jobs

    def scrape(self):
        jobs = self.scrape_job_links()

        for j in jobs:
            self.scrape_job_description(j)

        return jobs

        

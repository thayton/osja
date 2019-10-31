import time
import json
import logging
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qsl

class JuniperJobScraper(object):
    def __init__(self):
        self.url = 'https://careers.juniper.net/PSIGW/RESTListeningConnector/PSFT_HR/JN_REST_CR_KW_SRCH_SOP.v1/'
        self.payload = {
            'HRS_JO_PST_TYPE': 'E',
            'HRS_JO_TYPE': '',
            'BUSINESS_UNIT': 'USA01',
            'BUSINESS_UNIT_BD': '',
            'LOCATION': 0,
            'JOB_FAMILY': '',
            'DESCRLONG': ''
        }

        FORMAT = "%(asctime)s [ %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
        logging.basicConfig(format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.session = requests.Session()

    def scrape_job_description(self, job):
        assert job.get('url') != None, 'Job URL is not set'

        url_parts = urlparse(job['url'])

        jid = dict( parse_qsl(url_parts.query) )['jid']
        url = 'https://careers.juniper.net/PSIGW/RESTListeningConnector/PSFT_HR/JN_REST_CR_REQ_SRCH_SOP.v1/'
        
        payload = { 'HRS_JOB_OPENING_ID': jid }
        resp = self.session.post(url, json=payload, headers={
            'X-Requested-With': 'XMLHttpRequest'
        })
        data = resp.json()
        
        desc = data['JN_HRS_FLU_SITE']['DESCRLONG']
        soup = BeautifulSoup(desc, 'lxml')

        desc = [ t.split() for t in soup.find_all(text=True) ]
        desc = [ ' '.join(l) for l in desc if len(l) > 0 ]
        
        job['description'] = ' '.join(desc)
        return job['description']

    def scrape_job_links(self):
        assert self.url != None, 'Jobs page URL is not set'

        jobs = []
        resp = self.session.post(self.url, json=self.payload, headers={
            'X-Requested-With': 'XMLHttpRequest'
        })
        data = resp.json()

        jobs_list = data['JN_REST_CR_KW_SRCH_RES']['JN_REST_CR_PST_SRCH_COMP']

        for j in jobs_list:
            job = {}
            job['title'] = j['POSTING_TITLE']
            job['location'] = j['LOCATION_DESCR']
            job['url'] = f"https://careers.juniper.net/careers/careers/jobdescription.html?jid={j['HRS_JOB_OPENING_ID']}"
            jobs.append(job)
            
        return jobs

    def scrape(self):
        jobs = self.scrape_job_links()

        for j in jobs:
            self.scrape_job_description(j)

        return jobs

if __name__ == '__main__':
    scraper = JuniperJobScraper()
    jobs = scraper.scrape()
    print(json.dumps(jobs, indent=2))
        

        

import re
import json
import logging
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from requests import Request

class FlWaltonCountyJobScraper(object):
    def __init__(self):
        self.url = 'https://fl-waltoncounty.civicplushrms.com/careers/Jobs.aspx'
        self.session = requests.Session()

    def scrape_job_links(self):
        jobs = []

        resp = self.session.get(self.url)
        soup = BeautifulSoup(resp.text, 'lxml')

        r = re.compile(r'^grdOpenJobs_ctl\d+_ctl\d+_hlDetails$')

        # https://fl-waltoncounty.civicplushrms.com/careers/JobDetail.aspx?RequisitionId=50463
        for a in soup.find_all('a', id=r):
            x = {'class': 'jobListItem'}
            d = a.find_parent('div', attrs=x)

            job = {}
            job['title'] = d.b.text
            job['location'] = 'Fort Walton Beach, FL'
            job['url'] = urljoin(self.url, f"JobDetail.aspx?RequisitionId={a['data-id']}")

            jobs.append(job)

        return jobs

    def scrape_job_description(self, job):
        assert job['url'] != None, 'Job URL must be set'

        resp = self.session.get(job['url'])
        soup = BeautifulSoup(resp.text, 'lxml')

        d = soup.select_one('div#JobDetail')
        x = {'class': 'widget-content'}
        d = d.find_parent('div', attrs=x)

        job['description'] = str(d)

    def scrape(self):
        jobs = self.scrape_job_links()
        for j in jobs:
            self.scrape_job_description(j)

        print(json.dumps(jobs, indent=2))

if __name__ == '__main__':
    scraper = FlWaltonCountyJobScraper()
    scraper.scrape()
    

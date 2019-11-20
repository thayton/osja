import time
import json
import logging
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from osja.scrapers import JobScraper

class MojaJobScraper(JobScraper):
    def __init__(self):
        super(MojaJobScraper, self).__init__()
        self.url = 'https://moja.applicantstack.com/x/openings'

    def scrape_job_description(self, job):
        assert job.get('url') != None, 'Job URL is not set'

        resp = self.session.get(job['url'])
        soup = BeautifulSoup(resp.text, 'lxml')

        d = soup.select_one('div#ascontent')
        job['description'] = self.extract_text_from_soup(d)

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

if __name__ == '__main__':
    scraper = MojaJobScraper()
    jobs = scraper.scrape()
    print(json.dumps(jobs, indent=2))
        

        

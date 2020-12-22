import time
import json
import logging
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from requests import Request
from osja.scrapers import JobScraper

class InternetArchiveJobScraper(JobScraper):
    def __init__(self):
        super(InternetArchiveJobScraper, self).__init__()        
        self.url = 'http://internetarchive.applytojob.com/apply/jobs/'

    def scrape_job_links(self):
        jobs = []

        resp = self.session.get(self.url)
        soup = BeautifulSoup(resp.text, 'lxml')

        for a in soup.select('a.job_title_link'):
            tr = a.find_parent('tr')
            td = tr.find_all('td')
            
            job = {}
            job['title'] = a.text.strip()
            job['location'] = td[-1].text.strip()
            job['url'] = urljoin(self.url, a['href'])

            jobs.append(job)

        return jobs

    def scrape_job_description(self, job):
        assert job['url'] != None, 'Job URL must be set'

        resp = self.session.get(job['url'])
        soup = BeautifulSoup(resp.text, 'lxml')

        div = soup.select_one('div#job_view_wrapper')
        job['description'] = self.extract_text_from_soup(div)

        return job['description']

    def scrape(self):
        jobs = self.scrape_job_links()
        for j in jobs:
            self.scrape_job_description(j)

        print(json.dumps(jobs, indent=2))

if __name__ == '__main__':
    scraper = InternetArchiveJobScraper()
    scraper.scrape()
    

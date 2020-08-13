import time
import json
import logging
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from osja.scrapers import JobScraper

class MolexJobScraper(JobScraper):
    def __init__(self):
        super(MolexJobScraper, self).__init__()
        self.url = 'https://jobs.kochcareers.com/search/jobs/in'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36'
        }
        self.params = {
            'cfm10':  None,
            'cfm4': 'Molex',
            'location': None,
            'page': 1,
            'q': None
        }
        
    def scrape_job_description(self, job):
        assert job.get('url') != None, 'Job URL is not set'

        resp = self.session.get(job['url'], headers=self.headers)
        soup = BeautifulSoup(resp.text, 'lxml')

        div = soup.select_one('div.job__description')
        job['description'] = self.extract_text_from_soup(div)

        return job['description']

    def scrape_job_links(self):
        assert self.url != None, 'Jobs page URL is not set'
        
        jobs = []
        url = self.url

        while True:
            self.logger.info(f"Getting page {self.params['page']}")

            resp = self.session.get(url, headers=self.headers, params=self.params)
            soup = BeautifulSoup(resp.text, 'lxml')

            for a in soup.select('div.job h3 > a'):
                x = {'class': 'job__location'}
                d = a.find_next('div', attrs=x)
                
                job = {}
                job['title'] = a.text.strip()
                job['location'] = d.text.strip()
                job['url'] = urljoin(self.url, a['href'])

                jobs.append(job)

            next_page = soup.select_one('a.next_page')
            if next_page == None:
                break

            self.params['page'] += 1

        self.logger.info(f'Returning {len(jobs)} jobs')
        return jobs

    def scrape(self):
        jobs = self.scrape_job_links()

        for j in jobs:
            self.scrape_job_description(j)

        return jobs

if __name__ == '__main__':
    scraper = MolexJobScraper()
    jobs = scraper.scrape()
    print(json.dumps(jobs, indent=2))
        

        

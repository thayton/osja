import logging
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin

class NavyFederalJobScraper(object):
    def __init__(self):
        self.url = 'https://nfcucareers.ttcportals.com/jobs/search'
        self.params = {
            'ns_content': 'all_jobs',
            'page': 1            
        }

        FORMAT = "%(asctime)s [ %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
        logging.basicConfig(format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        
        self.session = requests.Session()
        
    def scrape_job_description(self, job):
        assert job.get('url') != None, 'Job URL is not set'

        resp = self.session.get(job['url'])
        html = f'<html><title>{resp.text}'        
        soup = BeautifulSoup(html, 'lxml')

        div = soup.select_one('div.job-description')
        job['description'] = div.text.strip()

        return job['description']

    def scrape_job_links(self):
        assert self.url != None, 'Jobs page URL is not set'

        jobs = []

        while True:
            self.logger.info(f"Getting page {self.params['page']}")

            # Weirdly the site returns HTML with the prefix HTML missing
            resp = self.session.get(self.url, params=self.params)
            html = f'<html><title>{resp.text}'
            soup = BeautifulSoup(html, 'lxml')

            for tr in soup.select('table.jobs_table tr.jobs_table_item'):
                a = tr.select_one('div.job_name > a')
                l = tr.select_one('td.job_location')
                l = l.text.split('-')[0]
                
                job = {}
                job['title'] = a.text.strip()
                job['url'] = urljoin(self.url, a['href'])
                job['location'] = l.strip()

                jobs.append(job)

            next_page = soup.select_one('div.pagination > a.next_page')
            if next_page is None:
                break

            self.params['page'] += 1

        return jobs

    def scrape(self):
        jobs = self.scrape_job_links()
        for j in jobs:
            self.scrape_job_description(j)
        
if __name__ == '__main__':
    scraper = NavyFederalJobScraper()
    scraper.scrape()

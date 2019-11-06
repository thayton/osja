import logging
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin

class CapstoneCorpJobScraper(object):
    def __init__(self):
        self.url = 'https://jobs-capstone.icims.com/jobs/search'
        self.params = {
            'ss': 1,
            'pr': 0,            
            'in_iframe': 1,
        }

        FORMAT = "%(asctime)s [ %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
        logging.basicConfig(format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        
        self.session = requests.Session()
        
    def scrape_job_description(self, job):
        assert job.get('url') != None, 'Job URL is not set'

        resp = self.session.get(job['url'])
        soup = BeautifulSoup(resp.text, 'lxml')

        div = soup.select_one('div.iCIMS_InfoMsg_Job')
        job['description'] = str(div)

        return job['description']

    def scrape_job_links(self):
        assert self.url != None, 'Jobs page URL is not set'

        jobs = []

        while True:
            self.logger.info(f"Getting page {self.params['pr'] + 1}")
            
            resp = self.session.get(self.url, params=self.params)
            soup = BeautifulSoup(resp.text, 'lxml')

            for li in soup.select('ul.iCIMS_JobsTable > li.row'):
                f = lambda t: t.name == 'span' and t.text.strip() == 'Job Location'
                sp1 = li.find(f)
                sp2 = sp1.find_next('span')
                a = li.select_one('div.title > a.iCIMS_Anchor')

                job = {}
                job['location'] = sp2.text.strip()
                job['url'] = urljoin(self.url, a['href'])
                job['title'] = a.find_all('span')[-1].text.strip()

                jobs.append(job)

            # On the last page the next page '>' link becomes invisible
            next_page = soup.find('span', attrs={ 'title': 'Next page of results' })
            if 'invisible' in next_page.parent.attrs['class']:
                break

            self.params['pr'] += 1

        self.logger.info(f'Returning {len(jobs)} jobs')
        return jobs

    def scrape(self):
        jobs = self.scrape_job_links()
        for j in jobs:
            self.scrape_job_description(j)
        
if __name__ == '__main__':
    scraper = CapstoneCorpJobScraper()
    scraper.scrape()
        

        

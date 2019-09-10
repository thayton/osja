import json
import logging
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin

class StrategyWiseJobScraper(object):
    def __init__(self):
        self.url = 'https://strategywise.bamboohr.com/jobs/'

        FORMAT = "%(asctime)s [ %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
        logging.basicConfig(format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.session = requests.Session()
        
    def scrape_job_description(self, job):
        assert job.get('url') != None, 'Job URL is not set'
        return job['description']

    def scrape_job_links(self):
        assert self.url != None, 'Jobs page URL is not set'

        jobs = []

        resp = self.session.get(self.url)
        soup = BeautifulSoup(resp.text, 'lxml')

        script = soup.select_one('script#positionData')
        data = json.loads(script.text)
        jobs_base_url = urljoin(self.url, '/jobs/view.php?id=%d')

        for k in data.keys():
            v = data[k]

            desc = BeautifulSoup(v['description'], 'lxml')

            job = {}
            job['title'] = v['jobOpeningName']
            job['location'] = v['location']['city'] + ', ' + v['location']['state']
            job['url'] = jobs_base_url % int(v['id'])
            job['description'] = desc.text.strip()

            jobs.append(job)

        return jobs

    def scrape(self):
        jobs = self.scrape_job_links()

        for j in jobs:
            self.scrape_job_description(j)

        return jobs

if __name__ == '__main__':
    scraper = StrategyWiseJobScraper()
    jobs = scraper.scrape()
    print(json.dumps(jobs, indent=2))
        

        

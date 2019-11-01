import time
import json
import logging
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin

class ArcadiaPowerJobScraper(object):
    def __init__(self):
        self.url = 'https://careers-page.workable.com/api/v1/accounts/arcadia-power/jobs'
        self.payload = {
            "query": "",
            "location": [],
            "department": [],
            "worktype": [],
            "remote": []
        }

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

        while True:
            resp = self.session.post(self.url, json=self.payload)            
            data = resp.json()

            for r in data['results']:
                l = r['location']
                loc = l['city'] + ', ' + l['region'] + ', ' + l['countryCode']

                soup = BeautifulSoup(r['description'], 'lxml')
                desc = [ t.split() for t in soup.find_all(text=True) ]
                desc = [ ' '.join(l) for l in desc if len(l) > 0 ]

                job = {}
                job['title'] = r['title']
                job['location'] = loc
                job['url'] = f"https://apply.workable.com/arcadia-power/j/{r['shortcode']}/"
                job['description'] = ' '.join(desc)

                jobs.append(job)

            next_page_token = data.get('nextPage')
            if next_page_token == None:
                break

            self.payload['token'] = next_page_token

        return jobs

    def scrape(self):
        jobs = self.scrape_job_links()

        for j in jobs:
            self.scrape_job_description(j)

        return jobs

if __name__ == '__main__':
    scraper = ArcadiaPowerJobScraper()
    jobs = scraper.scrape()
    print(json.dumps(jobs, indent=2))
        

        

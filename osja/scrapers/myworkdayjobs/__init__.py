import time
import json
import logging
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin

class MyWorkdayJobsJobScraper(object):
    def __init__(self):
        FORMAT = "%(asctime)s [ %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
        logging.basicConfig(format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.session = requests.Session()

    def scrape_job_description(self, job):
        assert job.get('url') != None, 'Job URL is not set'

        resp = self.session.get(job['url'], headers={
                'Accept': 'application/json,application/xml'
        })
        data = resp.json()
        desc = data['openGraphAttributes']['description']

        job['description'] = desc.strip()
        return job['description']

    def scrape_job_links(self):
        assert self.url != None, 'Jobs page URL is not set'

        jobs = []
        url = self.url
        total_num_jobs = None
        
        while True:
            resp = self.session.get(url, headers={
                'Accept': 'application/json,application/xml'
            })
            data = resp.json()

            children = data['body']['children']

            list_items = children[0]['children'][0]['listItems']
            end_points = children[0]['endPoints']
            
            for i in list_items:
                title = i['title']
                location = i['subtitles'][0]['instances'][0]['text']
                
                job = {}
                job['title'] = title['instances'][0]['text']
                job['location'] = location
                job['url'] = urljoin(self.url, title['commandLink'])

                jobs.append(job)
                
            pagination = next(ep for ep in end_points if ep.get('type') == 'Pagination')
            pagination_count = children[0]['facetContainer']['paginationCount']

            if total_num_jobs == None:
                total_num_jobs = int(pagination_count.get('value'))

            if len(jobs) >= total_num_jobs:
                break

            next_page = urljoin(self.url, pagination['uri']) + '/'
            url = urljoin(next_page, str(len(jobs)))
            
        return jobs

    def scrape(self):
        jobs = self.scrape_job_links()

        for j in jobs:
            self.scrape_job_description(j)

        return jobs        

        

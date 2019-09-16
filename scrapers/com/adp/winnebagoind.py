import time
import json
import logging
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse, urlencode, unquote

class WinnebagoJobScraper(object):
    def __init__(self):
        self.url = 'https://workforcenow.adp.com/mascsr/default/careercenter/public/events/staffing/v1/job-requisitions'
        self.params = {
            'cid': '82c90207-af7d-495b-b437-aa9a4c72f4e8',
            'timestamp': int(time.time()),
            'lang': 'en_US',
            'ccId': '19000101_000001',
            'locale': 'en_US',
            '$top': 20,
            #'$skip': 0
        }

        FORMAT = "%(asctime)s [ %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
        logging.basicConfig(format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.session = requests.Session()

    def make_job_url(self, job_id):
        '''
        Create and return job page URL given current URL and the jpid 
        extracted from the job link
        
        Parameters:
          job_id - External job id
        '''
        params = self.params.copy()

        del params['$top']
#        del params['$skip']

        params['timeStamp'] = int(time.time())

        url = urljoin(self.url, f'/mascsr/default/careercenter/public/events/staffing/v1/job-requisitions/{job_id}')

        url_parts = list(urlparse(url))
        url_parts[4] = urlencode(params)
        url_parts[4] = unquote(url_parts[4])

        url = urlunparse(url_parts)
        return url
        
    def scrape_job_description(self, job):
        assert job.get('url') != None, 'Job URL is not set'

        resp = self.session.get(job['url'], headers={
            'X-Requested-With': 'XMLHttpRequest'
        })
        data = resp.json()

        desc = BeautifulSoup(data['requisitionDescription'], 'lxml')
        job['description'] = desc.text.strip()

        return job['description']

    def scrape_job_links(self):
        assert self.url != None, 'Jobs page URL is not set'

        jobs = []

        while True:
            resp = self.session.get(self.url, params=self.params, headers={
                'X-Requested-With': 'XMLHttpRequest'
            })
            data = resp.json()

            if len(data['jobRequisitions']) == 0:
                break

            for j in data['jobRequisitions']:
                loc = 'Forest City, IA'
                locs = j['requisitionLocations']
                if len(locs) > 0:
                    loc = locs[0]['nameCode']['shortName']

                job_id = None

                for f in j['customFieldGroup']['stringFields']:
                    if f['nameCode']['codeValue'] == 'ExternalJobID':
                        job_id = f['stringValue']
                        break

                assert job_id != None, 'External Job ID not found'

                job = {}
                job['title'] = j['requisitionTitle']
                job['location'] = loc
                job['url'] = self.make_job_url(job_id)

                jobs.append(job)

            self.params['$skip'] = len(jobs) + 1

        return jobs

    def scrape(self):
        jobs = self.scrape_job_links()

        for j in jobs:
            self.scrape_job_description(j)

        return jobs

if __name__ == '__main__':
    scraper = WinnebagoJobScraper()
    jobs = scraper.scrape()
    print(json.dumps(jobs, indent=2))
        

        

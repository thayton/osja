import json
import time

from requests import Request
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from osja.scrapers import JobScraper

class CityOfPensacolaJobScraper(JobScraper):
    def __init__(self):
        super(CityOfPensacolaJobScraper, self).__init__()
        self.url = 'https://fl-pensacola.civicplushrms.com/CPExternal/Jobs.aspx'
        self.ajax_url = 'https://fl-pensacola.civicplushrms.com/CPExternal/CareerPortal.ashx'
        self.headers = {
            'X-Requested-With': 'XMLHttpRequest'
        }

        self.params = {
            'type': 'jobs',
            'clientId': None,
            '_': None
        }
        
    def scrape_job_links(self):
        jobs = []

        resp = self.session.get(self.url)
        soup = BeautifulSoup(resp.text, 'lxml')

        i = soup.select_one('input#hidClientId')
        client_id = i.get('value')

        def build_job_url(source_id, requisition_id):
            # CareerPortal.ashx?type=job&clientId=de5d567f-6331-4bb4-bbb3-dbff795d3556&sourceId=0&requisitionId=27284&_=1564511522605
            params = {
                'type': 'job',
                'clientId': client_id,
                'sourceId': source_id,
                'requisitionId': requisition_id,
                '_': int(time.time())
            }
            req = Request('GET', self.ajax_url, params=params).prepare()
            return req.url

        self.params['_'] = int(time.time())
        self.params['clientId'] = client_id
        
        resp = self.session.get(self.ajax_url, headers=self.headers, params=self.params)
        data = resp.json()

        for d in data:
            job = {}
            job['title'] = d['Title']
            job['location'] = d['PhysicalLocationNoZip']
            job['url'] = build_job_url(d['SourceId'], d['JobRequisitionId'])

            jobs.append(job)

        return jobs

    def scrape_job_description(self, job):
        assert job['url'] != None, 'Job URL must be set'

        resp = self.session.get(job['url'])
        data = resp.json()
        soup = BeautifulSoup(data[0]['JobDescription'], 'lxml')
        
        job['description'] = self.extract_text_from_soup(soup)
        
if __name__ == '__main__':
    scraper = CityOfPensacolaJobScraper()
    scraper.scrape()
    

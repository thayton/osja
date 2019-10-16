import re
import json
import logging
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

try:
    import urlparse
    from urllib import urlencode
except: # For Python 3
    import urllib.parse as urlparse
    from urllib.parse import urlencode

def extract_text(soup):
    text = soup.get_text()
    text = ' '.join( text.split() )
    return text

class AvionteJobScraper(object):
    def __init__(self):
        FORMAT = "%(asctime)s [ %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
        logging.basicConfig(format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.session = requests.Session()
        
    def scrape_job_description(self, job):
        assert job.get('url') != None, 'Job URL is not set'
        return job['description']

    def make_job_desc_url(self, job_post_id):
        url_parts = list(urlparse.urlparse(self.url))

        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update({ 'postid': job_post_id })

        url_parts[4] = urlencode(query)
        return urlparse.urlunparse(url_parts)
    
    def scrape_job_links(self):
        assert self.url != None, 'Jobs page URL is not set'

        jobs = []

        job_desc_api = 'https://hire.myavionte.com/sonar/v2/jobBoard/jobPost/{}/description'
        
        resp = self.session.get(self.url)
        soup = BeautifulSoup(resp.text, 'lxml')

        script = soup.find('script', id='compas-jobs-widget')
        build_id = script.attrs['data-bid']
        job_board_id = script.attrs['data-jbid']

        job_desc_headers = {
            'X-Compas-Careers-BuildIdEnc': build_id,
            'X-Compas-Careers-JobBoardIdEnc': job_board_id
        }

        resp = self.session.get(f'https://hire.myavionte.com/sonar/v2/jobBoard/{build_id}/{job_board_id}')
        data = resp.json()

        for k in data['jobPosts'].keys():
            j = data['jobPosts'][k]

            job = {}
            job['title'] = j['jobTitle']
            job['location'] = j['location']
            job['url'] = self.make_job_desc_url(j['jobPostIdEnc'])
            
            resp = self.session.get(job_desc_api.format(j['jobPostIdEnc']), headers=job_desc_headers)
            json_data = resp.json()
            desc = BeautifulSoup(json_data['description'], 'lxml')
            
            job['description'] = extract_text(desc)
            jobs.append(job)

        return jobs

    def scrape(self):
        jobs = self.scrape_job_links()

        for j in jobs:
            self.scrape_job_description(j)

        return jobs

if __name__ == '__main__':
    scraper = AvionteJobScraper()
    jobs = scraper.scrape()
    print(json.dumps(jobs, indent=2))
        

        

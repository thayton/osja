import logging
import requests

from bs4 import BeautifulSoup
from urllib import parse

class GovPredictJobScraper(object):
    def __init__(self):
        self.url = 'https://boards.greenhouse.io/embed/job_board'
        self.params = {
            'for': 'govpredict'
        }

        self.session = requests.Session()
        
    def scrape_job_description(self, job):
        assert job.get('url') != None, 'Job URL is not set'

        resp = self.session.get(job['url'])
        soup = BeautifulSoup(resp.text, 'lxml')

        div = soup.select_one('div#app_body')
        app = div.select_one('div#application')
        app.extract()

        job['description'] = str(div)

        return job['description']

    def make_job_url(self, job_link):
        # https://boards.greenhouse.io/embed/job_app?for=govpredict&token=4233934002
        jobs_base_url = 'https://boards.greenhouse.io/embed/job_app'        
        params = {
            'for': 'govpredict',
            'token': None
        }

        # https://govpredict.com/careers?gh_jid=4233934002
        query = dict(parse.parse_qsl(parse.urlsplit(job_link).query))
        params['token'] = query['gh_jid']

        url_parts = list(parse.urlparse(jobs_base_url))                     
        url_parts[4] = parse.urlencode(params)
        url_parts[4] = parse.unquote(url_parts[4])

        url = parse.urlunparse(url_parts)
        return url

    def scrape_job_links(self):
        assert self.url != None, 'Jobs page URL is not set'

        jobs = []
        
        resp = self.session.get(self.url, params=self.params)
        soup = BeautifulSoup(resp.text, 'lxml')

        for d in soup.select('div.opening'):
            a = d.a
            l = d.select_one('span.location').text

            job = {}
            job['title'] = a.text.strip()
            job['url'] = self.make_job_url(a['href'])
            job['location'] = l.strip()

            jobs.append(job)

        return jobs

    def scrape(self):
        jobs = self.scrape_job_links()
        for j in jobs:
            self.scrape_job_description(j)
        
if __name__ == '__main__':
    scraper = GovPredictJobScraper()
    scraper.scrape()
        

        

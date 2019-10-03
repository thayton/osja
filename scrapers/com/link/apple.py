import time
import json
import logging
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin

class AppleJobScraper(object):
    def __init__(self):
        self.url = 'https://jobs.apple.com/api/role/search'
        self.payload = {
            "query": "developer",
            "filters": {
                "range": {
                    "standardWeeklyHours": {
                        "start": None,
                        "end": None
                    }
                }
            },
            "page": 1,
            "locale": "en-us",
            "sort": "relevance"
        }

        FORMAT = "%(asctime)s [ %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
        logging.basicConfig(format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.session = requests.Session()

    def make_job_url(self, job_data):
        # t = e.countryCode.locale
        # d = "/" + t + "/details/" + a.positionId + "/" + a.transformedPostingTitle
        # a.team && a.team.teamCode && (d = d + "?team="+ a.team.teamCode)
        locale = job_data['localeInfo']['defaultLocaleCode']
        url = f"/{locale}/details/{job_data['positionId']}/{job_data['transformedPostingTitle']}"

        if job_data.get('team') and job_data['team'].get('teamCode'):
            url += f"?team={job_data['team']['teamCode']}"

        url = urljoin(self.url, url)

        return url

    def scrape_job_description(self, job):
        assert job.get('url') != None, 'Job URL is not set'

        resp = self.session.get(job['url'])
        soup = BeautifulSoup(resp.text, 'lxml')

        div = soup.select_one('div.job-details')
        job['description'] = div.text.strip()

        return job['description']

    def scrape_job_links(self):
        assert self.url != None, 'Jobs page URL is not set'

        jobs = []
        resp = self.session.get('https://jobs.apple.com/api/csrfToken')

        headers = {
            'X-Apple-CSRF-Token': resp.headers['X-Apple-CSRF-Token']
        }

        while True:
            resp = self.session.post(self.url, json=self.payload, headers=headers)
            data = resp.json()

            for j in data['searchResults']:
                locs = j['locations']
                if len(locs) == 0:
                    continue
                loc = locs[0]['name'] + ', ' + locs[0]['countryName']

                job = {}
                job['title'] = j['postingTitle']
                job['location'] = loc
                job['url'] = self.make_job_url(j)

                jobs.append(job)

            break
            
        return jobs

    def scrape(self):
        jobs = self.scrape_job_links()

        for j in jobs:
            self.scrape_job_description(j)

        return jobs

if __name__ == '__main__':
    scraper = AppleJobScraper()
    jobs = scraper.scrape()
    print(json.dumps(jobs, indent=2))
        

        

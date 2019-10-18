# ^fCPVycHKnwqL8LFASjJ9v_slp_rhc_QrU6iLO_slp_rhc_
# ^fCPVycHKnwqL8LFASjJ9v_slp_rhc_QrU6iLO_slp_rhc_/Cb0bu1AMA3bucmbWEA3wTN_slp_rhc_bclonn/nrsXoHOHFscv3O0WcydlP0Q8uDtAXy3SP9/c9raQUJDapw=
import time
import json
import logging
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qsl

class HuntingtonIngallsJobScraper(object):
    def __init__(self):
        # Derived classes have only to specify this initial URL
        self.url = 'https://sjobs.brassring.com/TGWebHost/home.aspx?partnerid=25477&siteid=5548'

        url_parts = urlparse(self.url)
        url_query = dict(parse_qsl(url_parts.query))

        self.payload = {
            'partnerId': url_query['partnerid'],
            'siteId': url_query['siteid'],
            'keyword': '',
            'location': '',
            'keywordCustomSolrFields': 'JobTitle,FORMTEXT17,FORMTEXT7,FORMTEXT1',
            'locationCustomSolrFields': 'FORMTEXT11,FORMTEXT16',
            'linkId': '',
            'Latitude': 0,
            'Longitude': 0,
            'facetfilterfields': {
                'Facet': []
            },
            'powersearchoptions': {
                'PowerSearchOption': []
            },
            'SortType': 'score',
            'pageNumber': 1,
            'encryptedSessionValue': None
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
        ajax_url = 'https://sjobs.brassring.com/TgNewUI/Search/Ajax/ProcessSortAndShowMoreJobs'
        
        resp = self.session.get(self.url)
        soup = BeautifulSoup(resp.text, 'lxml')
        
        cookie = soup.find('input', id='CookieValue')
        self.payload['encryptedSessionValue'] = cookie.get('value')

        def get_qval(job, name):
            q = next(filter(lambda q: q['QuestionName'] == name, job['Questions']), {})
            v = q.get('Value', None)
            if isinstance(v, str):
                return v.strip()
            else:
                return v

        while True:
            self.logger.info(f'Getting page {self.payload["pageNumber"]}')

            resp = self.session.post(ajax_url, json=self.payload)
            data = resp.json()

            if len(data['Jobs']['Job']) == 0:
                break

            for j in data['Jobs']['Job']:
                job = {}
                job['title'] = get_qval(j, 'jobtitle')
                job['location'] = get_qval(j, 'formtext11')
                job['url'] = j['Link']
                jobs.append(job)

            self.logger.info(f'{len(jobs)} jobs retrieved')
            self.payload['pageNumber'] += 1
            
        return jobs

    def scrape(self):
        jobs = self.scrape_job_links()

        for j in jobs:
            self.scrape_job_description(j)

        return jobs

if __name__ == '__main__':
    scraper = HuntingtonIngallsJobScraper()
    jobs = scraper.scrape()
    print(json.dumps(jobs, indent=2))
        

        

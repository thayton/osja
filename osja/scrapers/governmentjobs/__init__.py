import re
import json
import logging
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from requests import Request

class GovernmentJobsJobScraper(object):
    def __init__(self):
        self.params = {
            'action': 'jobs',
            'sortBy': 'CLASSIFICATION',
            'sortByASC': 'ASC',
            'bHideSearchBox': 1,
            'SEARCHAPPLIED': 0,
            'TRANSFER': 0,
            'PROMOTIONALJOBS': 0
        }
        self.data = {
            'pageCount': None,
            'sortBy': 'CLASSIFICATION',
            'sortOrder': 'ASC',
            'pageNumber': 1,
            'goToPage': 'go'
        }
        self.session = requests.Session()

    def scrape_job_links(self):
        assert hasattr(self, 'url'), 'URL not set'

        jobs = []

        resp = self.session.get(self.url)
        soup = BeautifulSoup(resp.text, 'lxml')

        i = soup.select_one('input#pageNumber_start')
        
        r = re.compile(r'\s+of\s+(\d+)')
        m = re.search(r, i.next)

        last_page = int(m.group(1))
        
        self.data['pageCount'] = last_page

        while True:
            resp = self.session.post(self.url, params=self.params, data=self.data)
            soup = BeautifulSoup(resp.text, 'lxml')

            for a in soup.select('table.NEOGOV_joblist a.jobtitle'):
                job = {}
                job['title'] = a.text
                job['url'] = urljoin(self.url, a['href'])

                jobs.append(job)

            # See if we've reached the last page - Page # <x> of <x>
            i = soup.select_one('input#pageNumber_start')
            curr_page = int(i['value'])

            if curr_page == last_page:
                break

            self.data['pageNumber'] += 1

        return jobs

    def scrape_job_description(self, job):
        assert job['url'] != None, 'Job URL must be set'

        resp = self.session.get(job['url'])
        soup = BeautifulSoup(resp.text, 'lxml')

        x = {'class': 'jobinfo'}
        th = soup.select_one('th.jobinfo')
        tb1 = th.find_parent('table')

        f = lambda t: t.name == 'th' and 'jobinfo' in t.attrs.get('class', []) and t.text.strip() == 'Location:'
        th = tb1.find(f)
        td = th.find_next('td')

        x = {'class': 'jobdetail', 'headers': 'viewJobDescription'}
        td = soup.find('td', attrs=x)
        tb2 = td.find_parent('table')

        # Different governmentjobs sites seem wrap header and detail in different
        # elems, sometimes divs, sometimes tables. Here we just extract the parts
        # we want and stuff them in an <html></html>
        html = BeautifulSoup("<html></html>", 'lxml')
        
        header = tb1.extract()        
        detail = tb2.extract()
        
        html.html.append(header)
        html.html.append(detail)
        
        job['location'] = td.text.strip()
        job['description'] = str(html)

    def scrape(self):
        jobs = self.scrape_job_links()
        for j in jobs:
            self.scrape_job_description(j)

        print(json.dumps(jobs, indent=2))    

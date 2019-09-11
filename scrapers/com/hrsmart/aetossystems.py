import json
import logging
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin

class AetosSystemsJobScraper(object):
    def __init__(self):
        self.url = 'https://aetossystems.hua.hrsmart.com/hr/ats/JobSearch/viewAll'
        self.url = 'https://aetossystems.hua.hrsmart.com/hr/ats/JobSearch/viewAll/jobSearchPaginationExternal_pageSize:10/jobSearchPaginationExternal_page:1'

        FORMAT = "%(asctime)s [ %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
        logging.basicConfig(format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        
        self.session = requests.Session()
        
    def scrape_job_description(self, job):
        assert job.get('url') != None, 'Job URL is not set'

        resp = self.session.get(job['url'])
        soup = BeautifulSoup(resp.text, 'lxml')

        div = soup.select_one('div#app_main_id > div.dtm-main-content > div#job-detail')
        job['description'] = div.text.strip()

        return job['description']

    def scrape_job_links(self):
        assert self.url != None, 'Jobs page URL is not set'
        pageno = 2
        jobs = []

        url = self.url

        while True:
            resp = self.session.get(url)
            soup = BeautifulSoup(resp.text, 'lxml')

            for a in soup.select('table#jobSearchResultsGrid_table td > a'):
                if a.span is None:
                    continue

                tr = a.find_parent('tr')
                td = tr.find_all('td')

                job = {}
                job['title'] = a.span.text.strip()                
                job['location'] = td[1].text.strip()
                job['url'] = urljoin(self.url, a['href'])

                jobs.append(job)

            # On the last page the next page '>' link becomes invisible
            f = lambda t: t.name == 'a' and 'paginateNumber' in t.attrs.get('class', []) and t.text == f'{pageno}'
            next_page = soup.find(f)
            if next_page == None:
                break

            url = urljoin(self.url, next_page['href'])

        return jobs

    def scrape(self):
        jobs = self.scrape_job_links()

        for j in jobs:
            self.scrape_job_description(j)

        return jobs

if __name__ == '__main__':
    scraper = AetosSystemsJobScraper()
    jobs = scraper.scrape()
    print(json.dumps(jobs, indent=2))

        

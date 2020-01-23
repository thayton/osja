import re
import json

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from osja.scrapers import JobScraper

class GulfCoSchoolsJobScraper(JobScraper):
    def __init__(self):
        super(GulfCoSchoolsJobScraper, self).__init__()
        self.url = 'https://ats3.atenterprise.powerschool.com/ats/job_board'
        self.params = {
            'COMPANY_ID': '00012150'
        }
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
        }
        

    def scrape_job_description(self, job):
        assert job.get('url') != None, 'Job URL is not set'

        resp = self.session.get(job['url'], headers=self.headers)
        soup = BeautifulSoup(resp.text, 'lxml')

        x = {'class': 'job-footer'}
        d = soup.find('div', attrs=x)
        d.extract()
        
        job['description'] = self.extract_text_from_soup(soup.html.body)
        return job['description']

    def scrape_job_links(self):
        assert self.url != None, 'Jobs page URL is not set'

        jobs = []
        resp = self.session.get(self.url, headers=self.headers, params=self.params)
        soup = BeautifulSoup(resp.text, 'lxml')

        d = soup.select_one('div#PageMainContainer')
        x = {'title': 'View'}
        
        for a in d.find_all('a', attrs=x):
            tr = a.find_parent('tr')
            td = tr.find_all('td')
            
            job = {}
            job['title'] = td[4].text.strip()
            job['location'] = 'Port St Joe, FL'
            job['url'] = urljoin(self.url, a['href'])

            jobs.append(job)
            
        return jobs

if __name__ == '__main__':
    scraper = GulfCoSchoolsJobScraper()
    jobs = scraper.scrape()
    print(json.dumps(jobs, indent=2))
        

        

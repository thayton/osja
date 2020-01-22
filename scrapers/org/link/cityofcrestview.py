import re
import json

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from osja.scrapers import JobScraper

class CityOfCrestviewJobScraper(JobScraper):
    def __init__(self):
        super(CityOfCrestviewJobScraper, self).__init__()
        self.url = 'https://www.cityofcrestview.org/Jobs.aspx'

    def scrape_job_description(self, job):
        assert job.get('url') != None, 'Job URL is not set'

        resp = self.session.get(job['url'])
        soup = BeautifulSoup(resp.text, 'lxml')

        r = re.compile(r"jobContentLoad\('\d+','','(\d+)'\)")
        m = re.search(r, resp.text)

        job_id = int(m.group(1))
        
        form = soup.select_one('form#aspnetForm')
        data = {
            'ctl00$ctl00$MainContent$scriptManager': 'ctl00$ctl00$MainContent$ModuleContent$ctl00$contentUpdatePanel|ctl00_ctl00_MainContent_ModuleContent_ctl00_contentUpdatePanel',
            '__EVENTTARGET': 'ctl00_ctl00_MainContent_ModuleContent_ctl00_contentUpdatePanel',
            '__EVENTARGUMENT': None,
            '__ASYNCPOST': True
            
        }
        post_url = urljoin(self.url, form['action'])
        
        for i in form.find_all('input'):
            if i.get('type') in [ 'submit', 'checkbox', 'radio' ]:
                continue
            
            k = i.get('name')
            if k:
                data[k] = i.get('value')

        for s in form.find_all('select'):
            k = s.get('name')
            if k:
                for o in s.find_all('option'):
                    if o.get('selected'):
                        data[k] = o.get('value')
                        break

        data['ctl00$ctl00$MainContent$ModuleContent$ctl00$hdnJobId'] = job_id
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
            'X-MicrosoftAjax': 'Delta=true',
            'X-Requested-With': 'XMLHttpRequest',
        }
        
        resp = self.session.post(post_url, headers=headers, data=data)
        
        r = re.compile(r'\|(\d+)\|updatePanel\|ctl00_ctl00_MainContent_ModuleContent_ctl00_contentUpdatePanel\|')
        m = re.search(r, resp.text)
        n = int(m.group(1))
        _,i = m.span(0)
        
        soup = BeautifulSoup(resp.text[i:i+n], 'lxml')
        
        div = soup.select_one('div#divJobContentListingDetails')
        job['description'] = self.extract_text_from_soup(div)

        return job['description']

    def scrape_job_links(self):
        assert self.url != None, 'Jobs page URL is not set'

        jobs = []
        resp = self.session.get(self.url)
        soup = BeautifulSoup(resp.text, 'lxml')

        form = soup.select_one('form#aspnetForm')
        data = {}
        post_url = urljoin(self.url, form['action'])
        
        for i in form.find_all('input'):
            k = i.get('name')
            if k:
                data[k] = i.get('value')

        resp = self.session.post(post_url, data=data)
        soup = BeautifulSoup(resp.text, 'lxml')

        r = re.compile(r'^jobTitle_\d+$')
        
        for a in soup.find_all('a', id=r):
            job = {}
            job['title'] = a.text.strip()
            job['location'] = 'Crestview, FL'
            job['url'] = urljoin(self.url, a['href'])

            jobs.append(job)
            
        return jobs

if __name__ == '__main__':
    scraper = CityOfCrestviewJobScraper()
    jobs = scraper.scrape()
    print(json.dumps(jobs, indent=2))
        

        

import json
import logging
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin

def extract_text(soup):
    text = soup.get_text()
    text = ' '.join( text.split() )
    return text

class UwfJobScraper(object):
    def __init__(self):
        self.url = 'https://nwfsc.interviewexchange.com/jobsearchfrm.jsp'

        FORMAT = "%(asctime)s [ %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
        logging.basicConfig(format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        
        self.session = requests.Session()
        
    def scrape_job_description(self, job):
        assert job['url'] is not None

        resp = self.session.get(job['url'])
        soup = BeautifulSoup(resp.text, 'html.parser')

        t = soup.find('table', id='printarea')
        job['description'] = extract_text(t)

    def submit_search(self):
        resp = self.session.get(self.url)
        soup = BeautifulSoup(resp.text, 'lxml')

        form = soup.find('form', attrs={ 'name': 'jobsrchfrm' })
        data = {
            '_csrf': None
        }

        for i in form.find_all('input'):
            if i.get('name') and i.get('type') != 'button':
                data[i['name']] = i.get('value')

        for s in form.find_all('select'):
            if s.get('name') is None:
                continue

            # Go with the first option if none are marked as selected
            options = s.find_all('option')
            data[s['name']] = options[0].get('value')

            for o in options:
                if o.get('selected'):
                    data[s['name']] = o.get('value')
                    break

        post_url = urljoin(self.url, form['action'])

        resp = self.session.post(post_url, data=data)
        return resp.text

    def scrape_job_listings(self):
        jobs = []

        html = self.submit_search()
        soup = BeautifulSoup(html, 'lxml')

        aloc = { 'data-column': 'Location' }
        ajob = { 'data-column': 'Job Title' }
        
        while True:
            table = soup.select_one('table#searchResultsTable')
            for td in table.find_all('td', attrs=ajob):
                a = td.a

                tr = td.find_parent('tr')
                td = tr.find('td', attrs=aloc)
                
                job = {}
                job['title'] = a.text.strip()
                job['url'] = urljoin(self.url, a['href'])
                job['location'] = td.text.strip()
                jobs.append(job)

            f = lambda t: t.name == 'a' and t.text.strip() == 'Next >>'
            next_page = soup.find(f)
            if next_page is None:
                break

            next_page_url = urljoin(self.url, next_page['href'])

            resp = self.session.get(next_page_url)
            soup = BeautifulSoup(resp.text, 'lxml')

        return jobs

    def scrape(self):
        jobs = self.scrape_job_listings()
        for j in jobs:
            self.scrape_job_description(j)

        print(json.dumps(jobs, indent=2))

if __name__ == '__main__':
    scraper = UwfJobScraper()
    scraper.scrape()
        

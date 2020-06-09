import logging
import requests
import argparse

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from osja.scrapers import JobScraper

class WsscWaterJobScraper(JobScraper):
    def __init__(self):
        super(WsscWaterJobScraper, self).__init__()
        self.url = 'https://wsscwater.peopleadmin.com/postings/search'

    def scrape_job_description(self, job):
        assert job.get('url') != None, 'Job URL is not set'

        resp = self.session.get(job['url'])
        soup = BeautifulSoup(resp.text, 'lxml')

        d = soup.select_one('div#form_view')

        job['description'] = self.extract_text_from_soup(d)
        return job['description']

    def scrape_job_links(self):
        jobs = []

        resp = self.session.get(self.url)
        soup = BeautifulSoup(resp.text, 'lxml')

        css_sel = 'div#search_results div.job-item div.job-title > h3 > a'
        for a in soup.select(css_sel):
            d = a.find_parent('div')

            d = d.find_next_sibling('div')
            d = d.find_all('div')

            l = d[-1].text.strip() + ', MD'
            
            job = {}
            job['title'] = a.text
            job['url'] = urljoin(self.url, a['href'])
            job['location'] = l
            jobs.append(job)
            
        self.logger.info(f'{len(jobs)} jobs scraped')
        return jobs
    
if __name__ == '__main__':
    scraper = WsscWaterJobScraper()
    scraper.scrape()


import json

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from osja.scrapers import JobScraper

class FrcJobScraper(JobScraper):
    def __init__(self):
        super(FrcJobScraper, self).__init__()
        self.url = 'https://www.frc.org/job-listings'

    def scrape_job_description(self, job):
        assert job.get('url') != None, 'Job URL is not set'

        resp = self.session.get(job['url'])
        soup = BeautifulSoup(resp.text, 'lxml')

        div = soup.select_one('div.fill-width-if-lt-desktop')
        job['description'] = self.extract_text_from_soup(div)

        return job['description']

    def scrape_job_links(self):
        assert self.url != None, 'Jobs page URL is not set'

        jobs = []
        resp = self.session.get(self.url)
        soup = BeautifulSoup(resp.text, 'lxml')
        
        for a in soup.select('ul.search-results > li > a'):
            job = {}
            job['title'] = a.text.strip()
            job['location'] = 'Washington, DC'
            job['url'] = urljoin(self.url, a['href'])

            jobs.append(job)
            
        return jobs

if __name__ == '__main__':
    scraper = FrcJobScraper()
    jobs = scraper.scrape()
    print(json.dumps(jobs, indent=2))
        

        

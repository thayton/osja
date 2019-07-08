import logging

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from osja.selenium import ElemWrapper, chrome_driver
from selenium.webdriver.common.by import By

class GulfStreamJobScraper(ElemWrapper):
    def __init__(self, driver):
        super(GulfStreamJobScraper, self).__init__(driver)
        self.url = 'https://career4.successfactors.com/career?company=GulfStrProd'

        FORMAT = "%(asctime)s [ %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
        logging.basicConfig(format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

    def set_max_jobs_per_page(self):
        l = self.find(by=(By.XPATH, '//label[text()="Items per page"]'))
        select_id = l.get_attribute('for')
        opts = self.get_select_options(select_id)
        self.select(select_id, opts[-1]['value'])

    def scrape_job_description(self, job):
        assert job.get('url') != None, 'Job URL is not set'

        self.driver.get(job['url'])

        div = self.wait_until_visible('jobAppPageTitle')
        sp = div.find(by=(By.XPATH, '//span[starts-with(text(),"Geographic Location")]'))
        sp.click()
        
        sp = self.wait_until_visible(by=(By.XPATH, '//span[@style="jobContentEM"]'))
        job['location'] = sp.text.strip()

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        div = soup.find('div', id='jobAppPageTitle')

        job['description'] = str(div)

    def scrape_job_links(self):
        assert self.url != None, 'Jobs page URL is not set'
        
        jobs = []

        self.driver.get(self.url)

        b = self.find(by=(By.XPATH, '//button[text()="Search Jobs"]'))
        b.click()
        b.wait_until_stale()

        td = self.wait_until_visible(by=(By.CSS_SELECTOR, 'div#careerJobSearchContainer td.jobSearchResults'))

        self.set_max_jobs_per_page()

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        for a in soup.select('tr.jobResultItem a.jobTitle'):
            job = {}
            job['title'] = a.text.strip()
            job['url'] = urljoin(self.url, a['href'])
            jobs.append(job)

        return jobs

    def scrape(self):
        jobs = self.scrape_job_links()
        for j in jobs:
            self.scrape_job_description(j)
        
if __name__ == '__main__':
    driver = chrome_driver(
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        '../../../bin/chromedriver'
    )
    scraper = GulfStreamJobScraper(driver)
    scraper.scrape()

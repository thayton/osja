import time
import json
import logging
import requests

from bs4 import BeautifulSoup, Comment
from urllib.parse import urljoin, urlparse, urlunparse, urlencode, unquote

class JobScraper(object):
    def __init__(self):
        FORMAT = "%(asctime)s [ %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
        logging.basicConfig(format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.session = requests.Session()

    def delay(self):
        time.sleep(0.5)

    def extract_text_from_soup(self, tag):
        for script in tag.find_all('script'):
            script.extract()

        for comment in tag.find_all(text=lambda text: isinstance(text, Comment)):
            comment.extract()

        desc = [ t.split() for t in tag.find_all(text=True) ]
        desc = [ ' '.join(l) for l in desc if len(l) > 0 ]
        desc = ' '.join(desc)

        return desc

    def scrape_job_description(self, job):
        raise NotImplementedError

    def scrape_job_links(self):
        raise NotImplementedError

    def scrape(self):
        jobs = self.scrape_job_links()

        for j in jobs:
            self.delay()
            self.scrape_job_description(j)

        return jobs
    

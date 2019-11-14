import json
from osja.scrapers.adp import AdpJobScraper

class SandestinJobScraper(AdpJobScraper):
    def __init__(self):
        self.cid = '22225e6b-dce9-4d7b-b261-ed975f56a8d2'
        super(SandestinJobScraper, self).__init__()

if __name__ == '__main__':
    scraper = SandestinJobScraper()
    jobs = scraper.scrape()
    print(json.dumps(jobs, indent=2))
        

        

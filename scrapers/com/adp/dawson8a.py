import json
from osja.scrapers.adp import AdpJobScraper

class DawsonJobScraper(AdpJobScraper):
    def __init__(self):
        self.cid = '8ca3105b-2a62-4f2f-88e4-a1c9a90fbb6e'
        super(DawsonJobScraper, self).__init__()

if __name__ == '__main__':
    scraper = DawsonJobScraper()
    jobs = scraper.scrape()
    print(json.dumps(jobs, indent=2))
        

        

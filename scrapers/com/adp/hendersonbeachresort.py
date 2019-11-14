import json
from osja.scrapers.adp import AdpJobScraper

class HendersonBeachResortJobScraper(AdpJobScraper):
    def __init__(self):
        self.cid = '03c7378b-60fd-4892-bc44-ca48d1b8bf00'
        super(HendersonBeachResortJobScraper, self).__init__()

if __name__ == '__main__':
    scraper = HendersonBeachResortJobScraper()
    jobs = scraper.scrape()
    print(json.dumps(jobs, indent=2))
        

        

import json
from osja.scrapers.adp import AdpJobScraper

class WinnebagoJobScraper(AdpJobScraper):
    def __init__(self):
        self.cid = '82c90207-af7d-495b-b437-aa9a4c72f4e8'
        super(WinnebagoJobScraper, self).__init__()

if __name__ == '__main__':
    scraper = WinnebagoJobScraper()
    jobs = scraper.scrape()
    print(json.dumps(jobs, indent=2))
        

        

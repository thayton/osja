import json
from osja.scrapers.avionte import AvionteJobScraper

class MinervaNetworksJobScraper(AvionteJobScraper):
    def __init__(self):
        super(MinervaNetworksJobScraper, self).__init__()
        self.url = 'https://www.minervanetworks.com/careers/'

if __name__ == '__main__':
    scraper = MinervaNetworksJobScraper()
    jobs = scraper.scrape()
    print(json.dumps(jobs, indent=2))
        

        

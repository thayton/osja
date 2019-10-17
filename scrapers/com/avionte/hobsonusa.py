import json
from osja.scrapers.avionte import AvionteJobScraper

class HobsonUsaJobScraper(AvionteJobScraper):
    def __init__(self):
        super(HobsonUsaJobScraper, self).__init__()
        self.url = 'https://hobsonusa.com/careers/'

if __name__ == '__main__':
    scraper = HobsonUsaJobScraper()
    jobs = scraper.scrape()
    print(json.dumps(jobs, indent=2))
        

        

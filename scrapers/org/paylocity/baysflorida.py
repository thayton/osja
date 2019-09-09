import json
from osja.scrapers.paylocity import PaylocityJobScraper

class BaysFloridaJobScraper(PaylocityJobScraper):
    def __init__(self):
        super(BaysFloridaJobScraper, self).__init__()        
        self.url = 'https://recruiting.paylocity.com/Recruiting/Jobs/List/2080'
        
if __name__ == '__main__':
    scraper = BaysFloridaJobScraper()
    jobs = scraper.scrape()
    print(json.dumps(jobs, indent=2))        

        

import json
from osja.scrapers.paylocity import PaylocityJobScraper

class GulfWindsJobScraper(PaylocityJobScraper):
    def __init__(self):
        super(GulfWindsJobScraper, self).__init__()
        self.url = 'https://recruiting.paylocity.com/Recruiting/Jobs/List/5496'
        
if __name__ == '__main__':
    scraper = GulfWindsJobScraper()
    jobs = scraper.scrape()
    print(json.dumps(jobs, indent=2))

        

import json
from osja.scrapers.myworkdayjobs import MyWorkdayJobsJobScraper

class WexIncJobScraper(MyWorkdayJobsJobScraper):
    def __init__(self):
        super(WexIncJobScraper, self).__init__()
        self.url = 'https://wexinc.wd5.myworkdayjobs.com/WEXInc'

if __name__ == '__main__':
    scraper = WexIncJobScraper()
    jobs = scraper.scrape()
    print(json.dumps(jobs, indent=2))
        

        

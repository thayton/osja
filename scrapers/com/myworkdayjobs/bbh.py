import json
from osja.scrapers.myworkdayjobs import MyWorkdayJobsJobScraper

class BbhJobScraper(MyWorkdayJobsJobScraper):
    def __init__(self):
        super(BbhJobScraper, self).__init__()
        self.url = 'https://bbh.wd5.myworkdayjobs.com/BBH/jobs'

if __name__ == '__main__':
    scraper = BbhJobScraper()
    jobs = scraper.scrape()
    print(json.dumps(jobs, indent=2))
        

        

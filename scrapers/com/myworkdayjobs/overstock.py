import json
from osja.scrapers.myworkdayjobs import MyWorkdayJobsJobScraper

class OverstockJobScraper(MyWorkdayJobsJobScraper):
    def __init__(self):
        super(OverstockJobScraper, self).__init__()
        self.url = 'https://overstock.wd5.myworkdayjobs.com/Overstock_Careers'

if __name__ == '__main__':
    scraper = OverstockJobScraper()
    jobs = scraper.scrape()
    print(json.dumps(jobs, indent=2))
        

        

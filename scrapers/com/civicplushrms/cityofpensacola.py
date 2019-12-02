import json
from osja.scrapers.civicplushrms import CivicPlusHrmsJobScraper

class CityOfPensacolaJobScraper(CivicPlusHrmsJobScraper):
    def __init__(self):
        super(CityOfPensacolaJobScraper, self).__init__()
        self.url = 'https://fl-pensacola.civicplushrms.com/CPExternal/Jobs.aspx'
        
if __name__ == '__main__':
    scraper = CityOfPensacolaJobScraper()
    jobs = scraper.scrape()
    print(json.dumps(jobs, indent=2))

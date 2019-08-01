from osja.scrapers.governmentjobs import GovernmentJobsJobScraper

class PowayJobScraper(GovernmentJobsJobScraper):
    def __init__(self):
        super(PowayJobScraper, self).__init__()
        self.url = 'https://agency.governmentjobs.com/poway/default.cfm'

if __name__ == '__main__':
    scraper = PowayJobScraper()
    scraper.scrape()
    

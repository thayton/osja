import argparse

from osja.scrapers.selectminds import SelectMindsJobScraper

class GeicoJobScraper(SelectMindsJobScraper):
    def __init__(self):
        super(GeicoJobScraper, self).__init__()
        self.url = 'https://geico.referrals.selectminds.com'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", help="Display debugging messages", action="store_true")
    
    scraper = GeicoJobScraper()
    args = parser.parse_args()

    if args.debug:
        scraper.logger.setLevel(logging.DEBUG)

    scraper.scrape()

if __name__ == '__main__':
    main()

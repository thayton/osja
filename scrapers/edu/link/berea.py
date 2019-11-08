import re
import json
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin

class BereaJobScraper(object):
    def __init__(self):
        self.session = requests.Session()        
        self.url = 'https://myberea.csod.com/ats/careersite/search.aspx'
        self.params = {
            'site': 1,
            'c': 'myberea'
        }

    def scrape_job_description(self, job):
        assert job['url'] is not None

        resp = self.session.get(job['url'])
        soup = BeautifulSoup(resp.text, 'html.parser')

        d = soup.find('div', id='form_view')

        job['description'] = d.text.strip()

    def submit_aspnet_form(self, soup, event_target):
        form = soup.find('form', id='aspnetForm')
        data = {
            'ctl00$ScriptManager': f'ctl00$siteContent$widgetLayout$rptWidgets$ctl00$widgetContainer$ctl00$ctl00|{event_target}',
            '__EVENTTARGET': event_target,
            '__EVENTARGUMENT': None,
            '__ASYNCPOST': 'true'
        }

        for i in form.find_all('input'):
            k = i.get('name')
            v = i.get('value')

            if k == None:
                continue
            
            if i.get('type') == 'radio':
                if i.get('checked') != None:
                    data[k] = v
            else:
                data[k] = v

        for s in form.find_all('select'):
            k = s.get('name')
            o = next((o for o in s.find_all('option') if o.get('selected')), {})
            v = o.get('value')
            
            if v != None:
                data[k] = v

        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
        }
        
        resp = self.session.post(self.url, params=self.params, data=data, headers=headers)
        data = {}

        for t in [ r'\|(\d+)\|updatePanel\|ctl00_siteContent_widgetLayout_rptWidgets_ctl00_widgetContainer_ctl00_ctl00\|',
                   r'\|(\d+)\|hiddenField\|__VIEWSTATE\|',
                   r'\|(\d+)\|hiddenField\|__VIEWSTATEGENERATOR\|',
                   r'\|(\d+)\|hiddenField\|__PREVIOUSPAGE\|' ]:
            r = re.compile(t)
            m = re.search(r, resp.text)

            n = int(m.group(1))
            _,e = m.span(0)

            fields = t.split('\|')

            elem_type = fields[2]
            elem_id = fields[-2]

            if elem_type == 'updatePanel':
                html = resp.text[e:e+n]
                new_tree = BeautifulSoup(html, 'lxml')
                
                old_tree = soup.find(id=elem_id)
                old_tree.replace_with(new_tree)
            else:
                elem = soup.find(id=elem_id)
                elem['value'] = resp.text[e:e+n]
            
        return soup

    def goto_page(self, soup, pageno):
        f = lambda t: t.name == 'a' and 'pagerLink' in t.attrs.get('class', []) and t.text.strip() == f'{pageno}'
        t = re.compile(r"__doPostBack\('([^']+)")
            
        next_page = soup.find(f)
        if next_page is None:
            return None

        m = re.search(t, next_page['href'])
        event_target = m.group(1)
        
        soup = self.submit_aspnet_form(soup, event_target)
        return soup
        
    def submit_search_form(self):
        resp = self.session.get(self.url, params=self.params)
        soup = BeautifulSoup(resp.text, 'lxml')

        event_target = 'ctl00$siteContent$widgetLayout$rptWidgets$ctl00$widgetContainer$ctl00$btnSearch'
        soup = self.submit_aspnet_form(soup, event_target)
        
        return soup

    def scrape_job_listings(self):
        jobs = []

        pageno = 2
        
        soup = self.submit_search_form()

        x = { 'class': 'CsLinkButton', 'id': re.compile(r'_linkResult') }
        r = re.compile(r'(JobDetails.aspx[^"]+)"')
        
        while True:
            for a in soup.find_all('a', attrs=x):
                m = re.search(r, a['href'])
                
                job = {}
                job['title'] = a.text.strip()
                job['url'] = urljoin(self.url, m.group(1))
                job['location'] = 'Berea, KY'
                jobs.append(job)

            soup = self.goto_page(soup, pageno)
            if soup == None:
                break
            
        return jobs

    def scrape(self):
        jobs = self.scrape_job_listings()
        for j in jobs:
            self.scrape_job_description(j)

        print(json.dumps(jobs, indent=2))

if __name__ == '__main__':
    scraper = BereaJobScraper()
    scraper.scrape()
        

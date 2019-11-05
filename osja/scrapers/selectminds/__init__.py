import re
import sys
import json
import time
import logging
import requests

from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin

class SelectMindsJobScraper(object):
    def __init__(self):
        FORMAT = "%(asctime)s [ %(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
        logging.basicConfig(format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.session = requests.Session()

    def guid(self):
        '''
        TVAPP.guid() creates a URL with the milliseconds portion of the current date 
        as a parameter to uid:
        
	  TVAPP.guid = function(url) {
	    var date = new Date
	    var uid = date.getMilliseconds();
	    var additionType = "?uid=";
        
	    for (var i = 0; i < url.length; i++) {
		    if(url.charAt(i) == '?') {
			    additionType = "&uid="
		    }
	    }
        
	    var newURL = url + additionType + uid;
            return newURL;
	 };
        '''
        dt = datetime.now()
        guid = dt.microsecond / 1000
        return guid

    def get_site_short_name(self, soup):
        x = { 'type': 'text/javascript' }
        r = re.compile(r'short_name:\s+"([^"]+)')
        m = None
        
        for script in soup.find_all('script', attrs=x):
            m = re.search(r, script.text)
            if m:
                break

        short_name = None
        
        if m:
            short_name = m.group(1)
            
        return short_name
        
    def get_tss_token(self, soup):
        i = soup.find('input', id='tsstoken')
        tss_token = i['value']

        return tss_token
    
    def get_job_search_id(self, tss_token):
        '''
        The click() handler on the main search form triggers the following code from
        job_search_banner.js:
        
        // Main submit binding
        j$('#jSearchSubmit', search_banner).click(function() {
          ...
          data['keywords'] = cat_val;
          ...
          j$.ajax({
	    type: 'POST',
	    url: TVAPP.guid('/ajax/jobs/search/create'),
	    data: data,
	    success: function(result){
		job_search_id = result.Result['JobSearch.id'];
		j$.log('job_search_id: ' + job_search_id);
		// Load results
		j$(document).trigger('loadSearchResults', {'job_search_id':job_search_id});
	    },
	    dataType: 'json',
	    error: function(xhr, textStatus, error) {
		TVAPP.masterErrorHandler(xhr, textStatus, error, null);
	    }
	 });

        The result of the AJAX call will be JSON data like the following:

        { 
          "Status":"OK",
          "UserMessage": "",
          "Result": {
            "JobSearch.id": 75462878
          }
        }
        '''
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'tss-token': tss_token,
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
        }
        
        uid = self.guid()
        params = {
            'uid': uid
        }
        
        data = {
            'keywords': ''
        }
        
        url = urljoin(self.url, '/ajax/jobs/search/create')

        resp = self.session.post(url, headers=headers, params=params, data=data)
        data = resp.json()

        return data['Result']['JobSearch.id']

    def load_search_results(self, tss_token, job_search_id, short_name, pageno=1):
        '''
        Mimic the call made by loadSearchResults(data). loadSearchResults() is defined in job_list.js

        https://eygbl.referrals.selectminds.com/ajax/content/job_results?JobSearch.id=41162473&page_index=1&site-name=default909&include_site=true&uid=436

	j$.ajax({
	    type: 'POST',
	    url: TVAPP.guid('/ajax/content/job_results?' + context + '&site-name=' + TVAPP.property.site.short_name + '&include_site=true'),
	    dataType: 'json',
            ...
        });

        The value of TVAPP.property.site.short_name is defined in the javascript code within one of the <script> tags
        on the main index page. Eg,
        
        TVAPP = TVAPP || {};
        TVAPP.property = {
          ...
          site: {
            id: "2",
            short_name: "default909"
          },
        '''
        headers = {
            'tss-token': tss_token,
        }

        params = {
            'JobSearch.id': job_search_id,
            'page_index': pageno,
            'site-name': short_name, # From TVAPP.property.site.short_name : short_name: "default909"
            'include_site': 'true',
            'uid': self.guid()
        }

        url = urljoin(self.url, '/ajax/content/job_results')

        resp = self.session.post(url, headers=headers, params=params)
        data = json.loads(resp.text)
        
        return data['Result']
    
    def scrape(self, filter_langs=[]):
        jobs = []
        
        resp = self.session.get(self.url)
        soup = BeautifulSoup(resp.text, 'lxml')
        
        tss_token = self.get_tss_token(soup)
        short_name = self.get_site_short_name(soup)

        job_search_id = self.get_job_search_id(tss_token)

        pageno = 1

        while True:
            self.logger.info(f'Getting page {pageno}')
            
            html = self.load_search_results(tss_token, job_search_id, short_name, pageno)
            soup = BeautifulSoup(html, 'html.parser')

            d = soup.find('div', id='job_results_list_hldr')
            
            x = {'class': 'job_link'}
            y = {'class': 'location'}
            
            for a in d.findAll('a', attrs=x):
                l = a.findNext('span', attrs=y)
            
                job = {}

                job['title'] = a.text
                job['url'] = urljoin(self.url, a['href'])
                job['location'] = l.text.strip()

                jobs.append(job)

            self.logger.info(f'{len(jobs)} jobs scraped')

            d = soup.find('div', id='jPaginateNumPages')
            num_pages = int(float(d.text))
            
            if pageno >= num_pages:
                break

            time.sleep(1) # Don't hit the server too quickly
            pageno += 1

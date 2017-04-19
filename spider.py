import os
import sys
import requests
import json
import re
from collections import namedtuple
from selenium import webdriver
from lxml import html


number_of_scraped = 0
total_count = 0

class Spider():
    main_page_url = 'https://searchicris.co.weld.co.us/recorder/web/login.jsp'
    wd = webdriver.PhantomJS(os.path.join(os.path.dirname(__file__), 'bin/phantomjs'))

    def __enter__(self):
        self.main_page()
        cookies = self.get_cookies()
        self.cookies = {'JSESSIONID': cookies['JSESSIONID'], 'f5_cspm': cookies['f5_cspm'],
                        'pageSize': '100', 'sortDir': 'asc', 'sortField': 'Document+Relevance'}
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.wd.quit()

    def get_cookies(self):
        return {cookie['name']: cookie['value']
                        for cookie in self.wd.get_cookies()
                        if '_ga' not in cookie['name']}

    def return_to_docsearch(self):
        self.wd.get('https://searchicris.co.weld.co.us/recorder/eagleweb/docSearch.jsp')

    def main_page(self):
        self.wd.get(self.main_page_url)
        self.wd.find_element_by_id('userId').send_keys() # login
        self.wd.find_element_by_name('password').send_keys() # password
        self.wd.find_elements_by_name('submit')[1].click()

    def pdf_link_by_doc_id(self, id):
        self.wd.find_element_by_id('DocumentNumberID').send_keys(id)
        self.wd.find_elements_by_xpath(".//div[@id='middle']//input")[0].click()
        hrefs = self.wd.find_elements_by_xpath(".//tr[@class='odd']//a")
        if hrefs:
            href = hrefs[0].get_attribute('href').split('=')[-1]
            url = 'https://searchicris.co.weld.co.us/recorder/eagleweb/downloads/' + id + '?id=' + href + '.A0&parent=' + href + '&preview=false&noredirect=true'
            return url
        return None

    def download(self, url):
        response = requests.get(url, cookies=self.cookies, stream=True)
        if response.status_code == 200:
            with open('./hello.pdf', 'wb') as f:
                response.raw.decode_content = True
                for chunk in response:
                    f.write(chunk)


if __name__ == '__main__':
    with Spider() as spider:
        link = spider.pdf_link_by_doc_id('3297223')
        spider.download(link)
    pass


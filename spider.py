import os
import requests
import csv
import tkinter
import time
from tkinter import filedialog
from selenium import webdriver

number_of_scraped = 0
started = False
delay = 0

class Spider():
    main_page_url = 'https://searchicris.co.weld.co.us/recorder/web/login.jsp'
    wd = webdriver.PhantomJS(os.path.join(os.path.dirname(__file__), 'bin/phantomjs'))

    def __init__(self, user, password):
        self.credentials = {'user' : user, 'password': password}

    def __enter__(self):
        self.main_page()
        cookies = self.get_cookies()
        self.cookies = {'JSESSIONID': cookies['JSESSIONID'], 'f5_cspm': cookies['f5_cspm'],
                        'pageSize': '100', 'sortDir': 'asc', 'sortField': 'Document+Relevance'}
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.wd.quit()

    def get_docs_id_from_csv(self, path, column):
        with open(path, 'r') as file:
            reader = csv.DictReader(file)
            return [row[column] for row in reader]

    def get_cookies(self):
        return {cookie['name']: cookie['value']
                        for cookie in self.wd.get_cookies()
                        if '_ga' not in cookie['name']}

    def return_to_docsearch(self):
        self.wd.get('https://searchicris.co.weld.co.us/recorder/eagleweb/docSearch.jsp')

    def main_page(self):
        self.wd.get(self.main_page_url)
        self.wd.find_element_by_id('userId').send_keys(self.credentials['user']) # login
        self.wd.find_element_by_name('password').send_keys(self.credentials['password']) # password
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

    def download(self, url, name, path):
        '''Name without extension'''
        response = requests.get(url, cookies=self.cookies, stream=True)
        if response.status_code == 200:
            with open(os.path.join(path, name + '.pdf'), 'wb') as f:
                response.raw.decode_content = True
                for chunk in response:
                    f.write(chunk)

def select_csv():
    global csv_path
    csv_path = filedialog.askopenfilename(**options)


def select_dir():
    global dir
    dir = filedialog.askdirectory()


def print_message():
    global number_of_scraped
    global started
    if started:
        input.delete(0, 'end')
        input.insert(0, 'Scraped ' + str(number_of_scraped))


def start():
    global number_of_scraped
    global started
    global delay
    delay = str(delay_inp.get())
    started = True
    col_name = input.get()
    with Spider(username_inp.get(), password_inp.get()) as spider:
        for doc_id in spider.get_docs_id_from_csv(csv_path, col_name):
            link = spider.pdf_link_by_doc_id(doc_id)
            spider.download(link, doc_id, '.')
            spider.return_to_docsearch()
            number_of_scraped += 1
            time.sleep(delay)


csv_path = ""
dir = ""
root = tkinter.Tk()
options = {}
options['defaultextension'] = '.csv'
options['initialdir'] = '.'
options['parent'] = root
options['title'] = 'Choose .csv file'
input = tkinter.Entry(root)
input.insert(0, 'Enter column name')
delay_inp = tkinter.Entry(root)
delay_inp.insert(0, 'Enter delay')
username_inp = tkinter.Entry(root)
username_inp.insert(0, 'Username')
password_inp = tkinter.Entry(root, show='*')
password_inp.insert(0, '123456')
start_btn = tkinter.Button(root, text='Start', command=start)
csv_btn = tkinter.Button(root, text='Select path to .csv', command=select_csv)
folder_btn = tkinter.Button(root, text='Select folder to save', command=select_dir)
username_inp.pack()
password_inp.pack()
csv_btn.pack()
folder_btn.pack()
input.pack()
start_btn.pack()
root.mainloop()










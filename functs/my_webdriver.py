from selenium import webdriver
from fake_useragent import UserAgent
import requests
def get_headers():
    ua = UserAgent()
    headers = {'User-Agent': ua.random, }
    return headers
def getBrowser(flag):
    chrome_options = webdriver.ChromeOptions()
    if flag==0:
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
    posC="C:\Download\small App\WebDriver\chromedriver.exe"
    b = webdriver.Chrome(executable_path=posC, options=chrome_options)
    return b


def is_element_exist(b, by, pos):
    s = b.find_elements(by, pos)
    if len(s) == 0:
        return False
    elif len(s) == 1:
        return True

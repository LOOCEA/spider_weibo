from fake_useragent import UserAgent
from requestium import Session
from selenium import webdriver

posC = "C:\Download\small App\WebDriver\chromedriver.exe"


def get_headers():
    ua = UserAgent()
    headers = {'User-Agent': ua.random, }
    return headers


def get_browser(flag):
    chrome_options = webdriver.ChromeOptions()
    if flag==0:
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
    b = webdriver.Chrome(executable_path=posC, options=chrome_options)
    return b


def get_session(flag):
    if flag == 0:
        return Session(webdriver_path=posC,
                       browser='chrome',
                       default_timeout=15,
                       webdriver_options={'arguments': ['headless', '--no-sandbox', '--disable-gpu']})
    else:
        return Session(webdriver_path=posC,
                       browser='chrome',
                       default_timeout=15,
                       )


def is_element_exist(browser, by, pos):
    s = browser.find_elements(by, pos)
    if len(s) == 0:
        return False
    elif len(s) == 1:
        return True

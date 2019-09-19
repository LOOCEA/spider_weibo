from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.action_chains import ActionChains
import re
import bs4
from functs import headless
from selenium.webdriver.support.ui import WebDriverWait
from requestium import  Keys
import traceback
#webdriverwait
from fake_useragent import UserAgent

def smart_wait(browser, by, pos):
    #  = WebDriverWait(browser, 10).until(EC.presence_of_element_located(locator))
    ele=WebDriverWait(browser, 10).until(lambda driver: driver.find_element(by, pos))
def get_distance(d1, d2):
    s=time.time()
    # browser = webdriver.Chrome()
    browser = headless.getBrowser()
    url="https://www.google.com/maps/dir/"
    browser.get(url)
    try:
        smart_wait(browser, By.XPATH, '//*[@id="sb_ifc50"]/input')
        smart_wait(browser,By.XPATH,'// *[ @ id = "omnibox-directions"] / div / div[2] / div / div / div[1] / div[4] / button')
        browser.find_element(By.XPATH,'// *[ @ id = "omnibox-directions"] / div / div[2] / div / div / div[1] / div[4] / button').click()
        browser.find_element(By.XPATH,'//*[@id="sb_ifc50"]/input').send_keys(d1)#'Australia rmit'
        ActionChains(browser).key_down(Keys.ENTER).key_up(Keys.ENTER).perform()
        browser.find_element(By.XPATH,'//*[@id="sb_ifc51"]/input').send_keys(d2)
        ActionChains(browser).key_down(Keys.ENTER).key_up(Keys.ENTER).perform()
        smart_wait(browser, By.CLASS_NAME, 'section-directions-trip-travel-mode-icon')
        soup=bs4.BeautifulSoup(browser.page_source,'lxml')
        soup= soup.find('div',class_="section-directions-trip-numbers")
        temp_str=soup.find_all('div')[1].getText()
        tmp_distance = re.findall('[\d+\.\d]*', temp_str)
        for i in tmp_distance:
            if i !='' :
                distance = i
                break
        if("米"  in temp_str or ('m' in temp_str and 'k' not in temp_str)):
            distance=float(float(distance) / 1000)
    except Exception as e:
        distance=-1
        print(traceback.print_exc())
        print('计算距离出错,Google map:',browser.current_url)

    finally:
        browser.close()
        e = time.time()
        # print('checking distance used', round(e - s, 2), 's')
        # print(float(distance))
        return float(distance)
# print(get_distance('Australia rmit','1909/8 Marmion Place, Docklands VIC, Australia'))


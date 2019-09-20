from functs import my_webdriver
import time
import random
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.action_chains import ActionChains
import re
import bs4
from functs.weibo_feed import WeiboFeed
from functs import my_webdriver
from selenium.webdriver.support.ui import WebDriverWait
from requestium import  Keys
import traceback
import requests
def smart_wait(browser, by, pos):
    #  = WebDriverWait(browser, 10).until(EC.presence_of_element_located(locator))
    ele = WebDriverWait(browser, 20).until(lambda driver: driver.find_element(by, pos))
def login(username, password, b):
    b.get('https://weibo.com/p/1005055218229072/')
    b.find_element(By.XPATH, '//*[@id="pl_common_top"]/div/div/div[3]/div[2]/ul/li[3]/a').click()
    wait(1)
    b.find_element(By.NAME, "username").send_keys(username)
    b.find_element(By.NAME, "password").send_keys(password)
    wait(1)
    b.find_element(By.CSS_SELECTOR, 'a[suda-data="key=tblog_weibologin3&value=click_sign"]').click()
    smart_wait(b, By.CSS_SELECTOR, 'a[action-type="select_year"]')
    print('login successfully')
    wait(5)
    b.execute_script("document.body.style.zoom='0.7'")
def find_content(b):
    for page in range(82, 100):
        # for i in range(10):
        #     b.execute_script("window.scrollTo(0, document.body.scrollHeight)");
        #     if is_element_exist(b,By.PARTIAL_LINK_TEXT, '下一页') is True:
        #         print('下拉完成')
        #         print('正在第'+str(page-1) +'页')
        #         break
        #     wait(2)
        # page_source=correct_decoding(b.page_source)
        page_source = b.page_source.replace('\n', '').encode('gbk', 'ignore').decode('gbk')
        soup = bs4.BeautifulSoup(page_source, 'lxml')
        feed_contents = soup.find_all('div', attrs={'class': 'WB_cardwrap WB_feed_type S_bg2 WB_feed_like'})
        for feed_content in feed_contents:
            if feed_content.find('span', attrs={'class': 'subtitle'}) is not None:  # ignore liked weibo
                continue
            feed = WeiboFeed()
            feed.url = b.current_url
            feed.username = feed_content.find('a',
                                              attrs={'suda-uatrack': 'key=noload_singlepage&value=user_name'}).getText()
            # get simple inf
            try:
                datetime_tool = feed_content.find('div', attrs={'class': 'WB_from S_txt2'})
                feed.datetime = datetime_tool.find_all('a')[0]['title']
                if len(datetime_tool.find_all('a')) != 1:
                    feed.tool = datetime_tool.find_all('a')[1].getText()
            except Exception as e:
                print('Failed to get tool or there is no tool')
                print(traceback.print_exc())
            try:
                feed.likes = feed_content.find_all('span', attrs={'node-type': 'like_status'})[-1].getText()
                if feed.likes == '赞':
                    feed.likes = 0
                feed.comments = feed_content.find_all('span', attrs={'node-type': 'comment_btn_text'})[-1].getText()
                if feed.comments == '评论':
                    feed.comments = 0
            except Exception as e:
                print('Failed to get likes or comments')
                print(traceback.print_exc())
            if feed_content.find('div', attrs={'class': 'WB_media_wrap clearfix'}) is not None:
                # img or video?
                feed_media = feed_content.find('div', attrs={'class': 'WB_media_wrap clearfix'})
                if feed_media.find('img') is not None:
                    # img
                    imgs = feed_media.find_all('img')
                    for img in imgs:
                        img_url = get_short_url(img['src'])
                        feed.img += img_url + ','
                else:
                    feed.video = get_short_url(feed_media.find('video')['src'])

            #     --------------start deprive detail--------------

            # judge if weibo is original
            if feed_content.find('div', attrs={'class': 'WB_feed_expand'}) is None:  # this is a original weibo
                feed.type = 'Original'
                feed.content = feed_content.find('div', attrs={'class': 'WB_text'}).getText().replace(' ', '')

            else:
                try:
                    feed.type = 'Forward'
                    forward_content = feed_content.find('div', attrs={'node-type': 'feed_list_forwardContent'})
                    feed.content = feed_content.find('div', attrs={'node-type': 'feed_list_content'}).getText().replace(
                        ' ', '') + " "
                    feed.forward_username = forward_content.find('div', attrs={'class': 'WB_info'}).getText().replace(
                        ' ', '').replace('@', '') + " "
                    feed.forward_content = forward_content.find('div', attrs={'class': 'WB_text'}).getText().replace(
                        ' ', '') + " "
                except Exception as e:
                    print('Failed to get content')
                    print(traceback.print_exc())
            try:
                feed.insert_into_table()
            except Exception as e:
                print('Failed to insert to the table')
                print(traceback.print_exc())
            print(feed.__dict__)
            print('------------------------')
        # next_page = b.find_element(By.PARTIAL_LINK_TEXT, '下一页')
        # ActionChains(b).move_to_element(next_page).click(next_page).perform()
        next_url = b.current_url
        if '&page=' in next_url:
            next_url = b.current_url.replace('&page=' + str(page - 1), '&page=' + str(page))
        else:
            next_url = next_url + '&page=' + str(page)
        b.get(next_url)
        print('successfully go to next page')

a=re.search(u'[\u4e00-\u9fa5]','http')
print(a)


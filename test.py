from functs import headless
import time
import random
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.action_chains import ActionChains
import re
import bs4
from functs.weibo_feed import WeiboFeed
from functs import headless
from selenium.webdriver.support.ui import WebDriverWait
from requestium import  Keys
import traceback
import requests
def find_by_month():
    file=open('ff.html','rb')
    soup=bs4.BeautifulSoup(file,'lxml')
    print(soup.getText())
    feed_contents=soup.find_all('div',attrs={'class':'WB_detail'})
    for feed_content in feed_contents:
        feed=weibo_feed()
        feed.username=feed_content.find('a',attrs={'suda-uatrack':'key=noload_singlepage&value=user_name'}).getText()
        feed.datetime=feed_content.find('a', attrs = {'node-type': 'feed_list_item_date'})['title']
        feed.tool=feed_content.find('a', attrs = {'action-type': 'app_source'}).getText()
        if feed_content.find('div', attrs = {'class': 'WB_feed_expand'}) is None:
        #     Original
            pass
        else:
            feed.content=feed_content.find('div', attrs = {'node-type': 'feed_list_content'}).getText()+" "+\
                         feed_content.find('div', attrs = {'node-type': 'feed_list_forwardContent'}).getText()
            print(feed.content)

# soup=bs4.BeautifulSoup('<div class="WB_from S_txt2"><a name="4416888077415154" target="_blank" href="/2494020804/I75kPv71g?from=page_1005055218229072_profile&amp;wvr=6&amp;mod=weibotime" title="2019-09-15 20:47" date="1568551641000" class="S_txt2" node-type="feed_list_item_date" suda-data="key=tblog_home_new&amp;value=feed_time:4416888077415154:fromprofile"> 9月15日 20:47</a> 来自 <a class="S_txt2" target="_blank" href="http://vip.weibo.com/prividesc?priv=1006&amp;from=feed">Android</a>            	            </div>','lxml')
# print(soup.find('div', attrs = {'class': 'WB_from S_txt2'}))
strr= '//weibo.com/p/1005055218229072/home?profile_ftype=1&is_all=1#_0'
# print(strr.split('/'))
def get_short_url(long_url):
    url='http://sa.sogou.com/gettiny?url='+long_url
    res=requests.get(url=url)
    return res.text
def get_big_pic_url(b,url):
    b.find_element(By.XPATH, '//img[@src='+url+']' ).click()
    wait(2)
    return b.find_element(By.XPATH, '//img[@class=asd]').get_property('src')
def tes(a,strr):
    print(strr)
strr='3小时前'
ans=re.findall('^[1-9]\d*',  strr)
def get_short_url(long_url):
    if 'https:' not in long_url:
        long_url='https:'+long_url
    url='http://suo.im/api.htm?url=urlencode(\'%s\')&key=5d822a01b1a9c722a6aa2c65@d5ca070c285c0854cf63c3b39d5237f1'% long_url
    # url='http://sa.sogou.com/gettiny?url='+long_url
    res=requests.get(url=url)
    return res.text
# print(get_short_url('//www.baidu.com'))

a=re.search(u'[\u4e00-\u9fa5]','http')
print(a)


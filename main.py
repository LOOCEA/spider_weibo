from functs import headless
from functs import weibo_feed
import re
import jsonpath
from PIL import Image
import json
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.action_chains import ActionChains
import bs4
from functs import headless
from selenium.webdriver.support.ui import WebDriverWait
import traceback
from functs.weibo_feed import WeiboFeed
import sys
import chardet
import requests
from io import BytesIO
def get_real_time(strr):
    t = time.time()
    if '分钟' in strr:
        ans=re.findall('^[1-9]\d*',  strr)
        t = time.time() - int(ans[0]) * 60
        return  time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t))
    elif '小时' in strr:
        ans = re.findall('^[1-9]\d*', strr)
        t = time.time() - int(ans[0]) * 60*60
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t))
    elif len(strr)<=5:
        return time.strftime('%Y-', time.localtime(t))+strr+' '+'00:00:00'
    elif len(strr)>5:
        return strr  + ' 00:00:00'


def is_element_exist(b,by,pos):
    s = b.find_elements(by,pos)
    if len(s) == 0:
        return False
    elif len(s) == 1:
        return True
def get_big_pic_url(b,url):
    print('//img[@src=\'%s\']' % url)
    img=b.find_element(By.XPATH, '//img[@src=\'%s\']'% url )
    ActionChains(b).move_to_element(img).move_by_offset(0,0).context_click().perform()
    wait(1)
    if is_element_exist(b,By.XPATH, '//img[@node-type=imgshow]'):
        big=b.find_element(By.XPATH, '//img[@node-type=imgshow]')
        ans=big.get_property('src')
        big.click()
        return ans
    else :
        big = b.find_element(By.XPATH, '//img[@dynamic-id]')
        ans = big.get_property('src')
        big.click()
        return ans
def get_short_url(long_url):
    urls=[]
    if 'https:' not in long_url and 'http' not in long_url:
        long_url='https:'+long_url

    urls.append('http://suo.im/api.htm?url=urlencode(%s)&key=5d822a01b1a9c722a6aa2c65@d5ca070c285c0854cf63c3b39d5237f1'% long_url)
    urls.append('http://tinyurl.com/api-create.php?url=%s' % long_url)
    print(long_url)
    for url in urls:
        res=requests.get(url=url)
        flag=re.search(u'[\u4e00-\u9fa5]',res.text)
        if flag is None and len(res.text)<40:
            return res.text
        continue
    return long_url
def correct_decoding(content):
    content=content.encode()
    typeEncode = sys.getfilesystemencoding()  ##系统默认编码
    infoencode = chardet.detect(content).get('encoding', 'utf-8')  ##通过第3方模块来自动提取网页的编码
    html = content.decode(infoencode, 'ignore').encode(typeEncode)  ##先转换成unicode编码，然后转换系统编码输出
    return html
def wait(n):
    time.sleep(n)
def find_content_by_json(id):
    json_url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=%s&containerid=107603%s' %(str(id),str(id))
    origin_url=json_url
    headers= headless.get_headers()
    for i in range(1,100):
        page='&page='+str(i)
        json_url=origin_url+page
        response= requests.get(json_url,headers = headers)
        dict = json.loads(response.text)
        cards = dict['data']['cards']
        for card in cards:
            feed = WeiboFeed()
            feed.type='Original'
            if card['card_type']==9:
                feed.url=get_short_url(card['scheme'])
                mblog=card['mblog']
                feed.blogid=mblog['id']
                if weibo_feed.is_mblog_existed(feed.blogid) ==True:
                    print('blog is repeated')
                    continue
                try:
                    feed.datetime=get_real_time(mblog['created_at'])
                    feed.content = mblog['text']
                    feed.comments= mblog['comments_count']
                    feed.likes = mblog['attitudes_count']
                    feed.reposts=mblog['reposts_count']
                    feed.tool=mblog['source']
                    user=mblog['user']
                    feed.username = user['screen_name']
                    feed.userid=user['id']
                except Exception as e:
                    print('Failed to get inf')
                    print(traceback.print_exc())
                try:
                    if jsonpath.jsonpath(card,'$..large')!=False:
                        # get imgs
                        imgs=jsonpath.jsonpath(card,'$..large')
                        img_url=''
                        for img in imgs:
                            img_url+=get_short_url(img['url']) +' ,'
                        feed.img=img_url
                    if jsonpath.jsonpath(card, '$..page_info') != False:
                        # get videos
                        video=jsonpath.jsonpath(card,'$..page_info')
                        feed.video =get_short_url(video[0]['page_url'])
                except Exception as e:
                    print('Failed to get imgs or video')
                    print(traceback.print_exc())
                try:
                    if 'retweeted_status' in mblog.keys():
                        # get retweeted content
                        feed.type = 'Forward'
                        retweeted_feed=mblog['retweeted_status']
                        feed.forward_userid = retweeted_feed['user']['id']
                        feed.forward_reposts=retweeted_feed['reposts_count']
                        feed.forward_likes=retweeted_feed['attitudes_count']
                        feed.forward_comments=retweeted_feed['comments_count']
                        feed.forward_content=retweeted_feed['text']
                        feed.forward_username=retweeted_feed['user']['screen_name']
                except Exception as e:
                    print('Failed to get retweeted weibo')
                    print(traceback.print_exc())
                feed.content=re.sub('<.*?>','',feed.content )
                feed.forward_content=re.sub('<.*?>','',feed.forward_content )
                feed.insert_into_table()
                print(feed.__dict__)
        print('go to page %s '% str(i+1))
        wait(1)
if __name__ == "__main__":
    id=6356377939
    find_content_by_json(id)

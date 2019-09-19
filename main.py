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
def find_content(b):
    for page in range(82,100):
        # for i in range(10):
        #     b.execute_script("window.scrollTo(0, document.body.scrollHeight)");
        #     if is_element_exist(b,By.PARTIAL_LINK_TEXT, '下一页') is True:
        #         print('下拉完成')
        #         print('正在第'+str(page-1) +'页')
        #         break
        #     wait(2)
        # page_source=correct_decoding(b.page_source)
        page_source = b.page_source.replace('\n','').encode('gbk', 'ignore').decode('gbk')
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
                if len(datetime_tool.find_all('a')) !=1:
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
                feed_media =feed_content.find('div', attrs={'class': 'WB_media_wrap clearfix'})
                if feed_media.find('img') is not None:
                    # img
                    imgs = feed_media.find_all('img')
                    for img in imgs:
                        img_url = get_short_url(img['src'])
                        feed.img += img_url + ','
                else:
                    feed.video= get_short_url(feed_media.find('video')['src'])


            #     --------------start deprive detail--------------

                # judge if weibo is original
            if feed_content.find('div', attrs={'class': 'WB_feed_expand'}) is None:  # this is a original weibo
                    feed.type='Original'
                    feed.content = feed_content.find('div', attrs={'class': 'WB_text'}).getText().replace(' ', '')

            else:
                try:
                    feed.type = 'Forward'
                    forward_content = feed_content.find('div', attrs={'node-type': 'feed_list_forwardContent'})
                    feed.content = feed_content.find('div', attrs={'node-type': 'feed_list_content'}).getText().replace(' ','') + " "
                    feed.forward_username = forward_content.find('div', attrs={'class': 'WB_info'}).getText().replace(' ', '').replace('@','')+ " "
                    feed.forward_content = forward_content.find('div', attrs={'class': 'WB_text'}).getText().replace(' ', '') + " "
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
            next_url=b.current_url.replace('&page='+str(page-1),'&page='+str(page))
        else:
            next_url =next_url+'&page='+str(page)
        b.get(next_url)
        print('successfully go to next page')
def wait(n):
    time.sleep(n)
def smart_wait(browser, by, pos):
    #  = WebDriverWait(browser, 10).until(EC.presence_of_element_located(locator))
    ele=WebDriverWait(browser, 20).until(lambda driver: driver.find_element(by, pos))
def login(username,password,b):
    b.get('https://weibo.com/p/1005055218229072/')
    b.find_element(By.XPATH,'//*[@id="pl_common_top"]/div/div/div[3]/div[2]/ul/li[3]/a').click()
    wait(1)
    b.find_element(By.NAME, "username").send_keys(username)
    b.find_element(By.NAME, "password").send_keys(password)
    wait(1)
    b.find_element(By.CSS_SELECTOR,'a[suda-data="key=tblog_weibologin3&value=click_sign"]').click()
    smart_wait(b,By.CSS_SELECTOR,'a[action-type="select_year"]')
    print('login successfully')
    wait(5)
    b.execute_script("document.body.style.zoom='0.7'")

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
    # username = '347733121@qq.com'
    # password = 'looceA5632329'
    # b = headless.getBrowser(1)
    # b.implicitly_wait(30)
    # login(username,password,b)
    # find_content(b)
    id=6356377939

    # json_url='https://m.weibo.cn/api/container/getIndex?refer_flag[]=0000015010_&refer_flag[]=0000015010_&from[]=feed&from[]=feed&loc[]=avatar&loc[]=avatar&is_all[]=1&is_all[]=1&jumpfrom=weibocom&sudaref=weibo.com&type=uid&value=5218229072&containerid=1076035218229072'
    find_content_by_json(id)

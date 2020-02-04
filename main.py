import json
import re
import time
import traceback

import jsonpath
import requests

from functs import my_spider
from functs import my_webdriver
from functs import weibo_feed
from functs.weibo_feed import WeiboFeed


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
def wait(n):
    time.sleep(n)
def find_content_by_json(id):
    json_url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=%s&containerid=107603%s' %(str(id),str(id))
    origin_url=json_url
    headers = my_webdriver.get_headers()
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
                feed.url = my_spider.get_short_url(card['scheme'])
                mblog=card['mblog']
                feed.blogid=mblog['id']
                if weibo_feed.is_row_existed(feed.blogid) == True:
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
                            img_url += my_spider.get_short_url(img['url']) + ' ,'
                        feed.img=img_url
                    if jsonpath.jsonpath(card, '$..page_info') != False:
                        # get videos
                        video=jsonpath.jsonpath(card,'$..page_info')
                        feed.video = my_spider.get_short_url(video[0]['page_url'])
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
    id = 0
    find_content_by_json(id)

import sys
import chardet
import requests
import re


def correct_decoding(content):
    content = content.encode()
    typeEncode = sys.getfilesystemencoding()  ##系统默认编码
    infoencode = chardet.detect(content).get('encoding', 'utf-8')  ##通过第3方模块来自动提取网页的编码
    html = content.decode(infoencode, 'ignore').encode(typeEncode)  ##先转换成unicode编码，然后转换系统编码输出
    return html


def get_short_url(long_url):
    services = []
    if 'https:' not in long_url and 'http' not in long_url:
        long_url = 'https:' + long_url
    services.append(
        'http://suo.im/api.htm?url=urlencode(%s)&key=5d822a01b1a9c722a6aa2c65@d5ca070c285c0854cf63c3b39d5237f1' % long_url)
    services.append('http://tinyurl.com/api-create.php?url=%s' % long_url)
    print(long_url)
    for service in services:
        res = requests.get(url=service)
        flag = re.search(u'[\u4e00-\u9fa5]', res.text)
        if flag is None and len(res.text) < 40:
            return res.text
        continue
    return long_url

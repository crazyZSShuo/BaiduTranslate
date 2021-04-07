import execjs
import requests
import re

session = requests.Session()

def get_response(keywords, sign, token):
    url = "https://fanyi.baidu.com/v2transapi?from=zh&to=en"
    headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
        "Host": "fanyi.baidu.com",
        "Origin": "https://fanyi.baidu.com",
        "Referer": "https://fanyi.baidu.com/",
    }
    data = {
        "from": "zh",
        "to": "en",
        "query": keywords,
        "transtype": "realtime",
        "simple_means_flag": "3",
        "sign": sign,
        "token": token,
        "domain": "common",
    }
    resp = session.post(url, data=data, headers=headers).json()
    return resp.get("trans_result",'').get("data",'')[0].get('dst')

def get_gtk_and_token(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
        "Host": "fanyi.baidu.com",
        "Referer": "https://fanyi.baidu.com/",
    }
    # token为空表示第一次访问百度网站服务器端没有收到baiduid cookie，会导致翻译接口校验不通过，通过刷新解决
    session.get(url, headers=headers)
    second_res = session.get(url, headers=headers).text
    comp_token = re.compile("token: '(.*?)',", re.S)
    comp_gtk = re.compile("gtk = '(.*?)';", re.S)
    # print(second_res)
    token = re.search(comp_token, second_res)
    gtk = re.search(comp_gtk, second_res)
    if not token:
        return
    if not gtk:
        return
    token = token.groups()[0]
    gtk = gtk.groups()[0]
    print(token,gtk)
    return token, gtk



def get_sign(strr, gtk):
    with open('./sign.js', 'r', encoding='UTF-8') as f:
        js = f.read()
    doc = execjs.compile(js)
    result = doc.call("get_sign", strr, gtk)
    print("Sign:", result)
    return result


if __name__ == '__main__':
    keywords = "今天天气不坏"
    start_url = "https://fanyi.baidu.com/"
    token, gtk = get_gtk_and_token(start_url)
    sign = get_sign(keywords, gtk)
    print("token:", token)
    print("gtk:", gtk)
    print("sign:", sign)
    result = get_response(keywords, sign, token)
    print(result)


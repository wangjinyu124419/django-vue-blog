# coding=utf-8
# 该代码示例适用于Python3
from urllib import parse

import requests


def md5(str):
    import hashlib
    m = hashlib.md5()
    m.update(str.encode("utf8"))
    return m.hexdigest()


statusStr = {
    '0': '短信发送成功',
    '-1': '参数不全',
    '-2': '服务器空间不支持,请确认支持curl或者fsocket,联系您的空间商解决或者更换空间',
    '30': '密码错误',
    '40': '账号不存在',
    '41': '余额不足',
    '42': '账户已过期',
    '43': 'IP地址限制',
    '50': '内容含有敏感词'
}

smsapi = "http://api.smsbao.com/"
# 短信平台账号
user = "freeshare"
# 短信平台密码
password = md5('12#$ffJJ2307')
# 要发送的短信内容
content = '【freeshare】您的验证码为:1234，5分钟内有效'
# 要发送短信的手机号码
phone = '6001135191916'

data = parse.urlencode({'u': user, 'p': password, 'm': phone, 'c': content})
send_url = smsapi + 'sms?' + data
# response = urllib.request.urlopen(send_url)
the_page = requests.get(send_url).json()
print(type(the_page))
# print(response.json())
# print(response.content)
# print()
# the_page = response.read().decode('utf-8')
print(statusStr[str(the_page)])

import re

from tornado.escape import linkify

url_pattern = re.compile(r'(?:https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]')

# 匹配模式
a_pattern = re.compile('<a href=.*?>.*?</a>')  # 匹配模式


def url_to_hyperlink(content: str):
    temp_content = a_pattern.sub("", content)
    urls = url_pattern.findall(temp_content)
    for url in urls:
        hyperlink = linkify(url, extra_params='target="_blank"')
        content = content.replace(url, hyperlink)
    return content

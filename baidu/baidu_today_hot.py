import time

import requests
from bs4 import BeautifulSoup as bs


# 浏览器头信息
class baidu_today_hot:
    header = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 ' \
             '(KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36'

    # 获取今日热点
    def today_hot(self):
        lists = []
        url = 'https://baike.baidu.com/'
        headers = {'User-Agent': self.header}
        r = requests.get(url, headers=headers)
        r = r.text
        html = bs(r)
        # 百度百科 热搜词条 今天
        today = html.find(attrs={'class': 'today content show'})
        # print(today)
        aa = today.find_all('a')
        for a in aa:
            href = a['href']
            lists.append(href)
            # print(a['href'])
        return lists

    # 获取热点内容
    def get_content(self):
        headers = {'User-Agent': self.header}
        lists = baidu_today_hot.today_hot(self)
        dicts = []
        for url in lists:
            print(url)
            r = requests.get(url, headers=headers)
            r.encoding = 'Unicode'
            r = r.text
            html = bs(r)
            # 获取标题
            title = html.find(attrs={'class': 'lemmaWgt-lemmaTitle-title'})
            h1 = title.find('h1')
            print(h1.text)
            h1 = str(h1.text)
            # 获取内容 lemma-summary
            temp = html.find(attrs={'class': 'lemma-summary'})
            contents = temp.find_all(attrs={'class': 'para'})
            content = ''
            for string in contents:
                content = content + string.text
            print(content)
            dicts = {h1: content}
            time.sleep(1)
        return dicts


if __name__ == '__main__':
    hot = baidu_today_hot()
    hot.get_content()

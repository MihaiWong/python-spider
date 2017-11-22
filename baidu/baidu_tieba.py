import re
import time

import requests
from bs4 import BeautifulSoup


class baidu_tieba:
    header = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
             'Chrome/61.0.3163.91 Safari/537.36'

    # 获取所有话题链接
    def baidu_url(self, baidu_url):
        headers = {'User-Agent': self.header}
        r = requests.get(baidu_url, headers=headers)
        print(r.status_code)
        r = r.text
        # print(r)
        count = re.compile(r'<span class="red_text">(.*?)</span>个，贴子数.*')
        number = re.search(string=r, pattern=count)
        print(number.group(1))
        number = number.group(1)
        url_lists = baidu_tieba.all_page(str(number), baidu_url)
        return url_lists

    # 获取所有贴子链接
    def tieba(self, baidu_url):
        headers = {'User-Agent': self.header}
        array = []
        nurls = baidu_tieba.baidu_url(baidu_url)
        for nurl in nurls:
            r = requests.get(nurl, headers=headers)
            print(r.status_code)
            r = r.text
            pattern = re.compile(r'<a href="(.*?)".*title="(.*?)".*class="j_th_tit ".*')
            res = re.findall(string=r, pattern=pattern)
            print(len(res))
            for result in res:
                print(result[0], result[1])
                new_url = 'https://tieba.baidu.com' + result[0]
                # print(new_url)
                array.append(new_url)
            time.sleep(0.5)
        return array

    # 每50 分一页
    def pagination(num):
        self = int(num)
        if self % 50 == 0:
            page = self // 50
            print(page)
            return page
        else:
            page = self // 50 + 1
            print(page)
            return page

    # 找到所有贴子分页
    def all_page(num, baidu_url):
        number = baidu_tieba.pagination(num)
        array = map(lambda x: (x - 1) * 50, range(1, number + 1))
        # print(list(array))
        array = list(array)
        address = map(lambda x: (baidu_url + '&pn=' + str(x)), array)
        address = list(address)
        # print(address)
        return address

    # 获取贴子所有楼层内容
    def get_content(self, baidu_url):
        headers = {'User-Agent': self.header}
        tbs = baidu_tieba.tieba(baidu_url)
        for tb in tbs:

            r = requests.get(tb, headers=headers)
            print(r.status_code)
            r = r.text
            count = re.compile(r'<span class="red">(.*?)</span>页.*')
            number = re.search(string=r, pattern=count)
            print(number.group(1))
            # 分页
            number = int(number.group(1))
            # 判断重复
            pnlist = []
            for i in range(1, number + 1):
                tb_url = tb + "?pn=" + str(i)
                if tb_url in pnlist and len(pnlist) > 0:
                    break
                else:
                    req = requests.get(tb_url, headers=headers)
                    print(req.status_code)
                    rr = req.text
                    html1 = BeautifulSoup(rr)
                    # 获取帖子标题
                    left_section = html1.find(attrs={"class": "left_section"})
                    try:
                        h3 = left_section.find('h3')
                        title = h3.get('title')
                    except Exception as e:
                        print(e)
                        h3 = left_section.find('h1')
                        title = h3.get('title')
                    print('title:')
                    print(title)

                    # 获取每层楼的内容
                    contents = html1.select('.d_post_content.j_d_post_content')
                    print(len(contents), '.....')
                    for content in contents:
                        print('内容:')
                        print(content.text)
                        print('----------')

                    # 获取层主名称
                    authors = html1.select('.p_author_name.j_user_card')
                    print(len(authors))
                    for author in authors:
                        print('层主:')
                        print(author.text)
                        print('----------')

                    # 获取发帖时间
                    times = html1.find_all(attrs={'class': 'tail-info'})
                    print(len(times))
                    for current in times:
                        # 用于判断时间
                        if len(current.text) == 16:
                            print('时间:')
                            print(current.text)
                        else:
                            pass
                        print('----------')

                    time.sleep(0.5)
                    print('****************')
        return 0


if __name__ == '__main__':
    baidu_url = 'https://tieba.baidu.com/f?kw=%E6%B2%AA%E4%B8%9C%E4%B8%AD%E5%8D%8E&ie=utf-8'
    baidu_tieba.get_content(baidu_url)
    # print(len(tieba(baidu_url)))

import requests
from bs4 import BeautifulSoup

# 兼容python2
try:
    import cookielib  # python2
except:
    import http.cookiejar as cookielib
import re
import time
import os.path

try:
    from PIL import Image
except:
    pass

# 构造 Request headers 使用手机端伪造头信息 绕过文字验证码
agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_0_2 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) ' \
        'Version/10.0 Mobile/14A456 Safari/602.1'
headers = {
    "Host": "www.zhihu.com",
    "Referer": "https://www.zhihu.com/",
    'User-Agent': agent
}

# 使用登录cookie信息
session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename='cookies')
try:
    session.cookies.load(ignore_discard=True)
except:
    print("Cookie 未能加载")


# def get_xsrf():
#     '''_xsrf 是一个动态变化的参数'''
#     index_url = 'https://www.zhihu.com'
#     # 获取登录时需要用到的_xsrf
#     index_page = session.get(index_url, headers=headers)
#     html = index_page.text
#     pattern = r'name="_xsrf" value="(.*?)"'
#     # 这里的_xsrf 返回的是一个list
#     _xsrf = re.findall(pattern, html)
#     return _xsrf[0]

def get_xsrf():
    url = 'https://www.zhihu.com'
    response = session.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    # <input type="hidden" name="_xsrf" value="0448114b8b68c194d9fc9d831d251379">
    tag = soup.find('input', attrs={'name': '_xsrf'})
    return tag['value']


# 获取验证码
def get_captcha():
    t = str(int(time.time() * 1000))
    captcha_url = 'https://www.zhihu.com/captcha.gif?r=' + t + "&type=login"
    r = session.get(captcha_url, headers=headers)
    with open('captcha.jpg', 'wb') as f:
        f.write(r.content)
        f.close()
    # 用pillow 的 Image 显示验证码
    # 如果没有安装 pillow 到源代码所在的目录去找到验证码然后手动输入
    try:
        im = Image.open('captcha.jpg')
        im.show()
        im.close()
    except:
        print(u'请到 %s 目录找到captcha.jpg 手动输入' % os.path.abspath('captcha.jpg'))
    captcha = input("please input the captcha\n>")
    return captcha


def isLogin():
    # 通过查看用户个人信息来判断是否已经登录
    url = "https://www.zhihu.com/settings/profile"
    login_code = session.get(url, headers=headers, allow_redirects=False).status_code
    if login_code == 200:
        return True
    else:
        return False


def login(secret, account):
    _xsrf = get_xsrf()
    headers["X-Xsrftoken"] = _xsrf
    headers["X-Requested-With"] = "XMLHttpRequest"
    # 通过输入的用户名判断是否是手机号
    if re.match(r"^1\d{10}$", account):
        print("手机号登录 \n")
        post_url = 'https://www.zhihu.com/login/phone_num'
        postdata = {
            '_xsrf': _xsrf,
            'password': secret,
            'phone_num': account
        }
    else:
        if "@" in account:
            print("邮箱登录 \n")
        else:
            print("你的账号输入有问题，请重新登录")
            return 0
        post_url = 'https://www.zhihu.com/login/email'
        postdata = {
            '_xsrf': _xsrf,
            'password': secret,
            'email': account
        }
    # 不需要验证码直接登录成功
    login_page = session.post(post_url, data=postdata, headers=headers)
    login_code = login_page.json()
    if login_code['r'] == 1:
        # 不输入验证码登录失败
        # 使用需要输入验证码的方式登录
        postdata["captcha"] = get_captcha()
        login_page = session.post(post_url, data=postdata, headers=headers)
        login_code = login_page.json()
        print(login_code['msg'])
    # 保存 cookies 到文件，
    # 下次可以使用 cookie 直接登录，不需要输入账号和密码
    session.cookies.save()


# try:
#     input = raw_input()
# except:
#     pass

# 获取话题的所有链接
def get_question_url(key):
    url = 'https://www.zhihu.com/search?type=content&range=3m&q=' + key
    r = session.get(url, headers=headers, allow_redirects=False)
    r = r.text
    html = BeautifulSoup(r)
    contents = html.select('.item.clearfix')
    list_url = []
    for content in contents:
        time.sleep(0.5)
        # print(content.find('a', attrs={'class': 'js-title-link'}).text)
        href = content.find('a', attrs={'class': 'js-title-link'})['href']
        href = get_full_website(href, 'https://www.zhihu.com')
        list_url.append(href)
        # print('----------')
    print(list(set(list_url)))
    return list(set(list_url))


# 获取话题内容和答案
def get_answer(key):
    header = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
             'Chrome/61.0.3163.91 Safari/537.36'
    head = {'User-Agent': header}
    list_urls = get_question_url(key)
    for list_url in list_urls:
        time.sleep(1)
        if 'zhuanlan.zhihu.com' in list_url:
            r = session.get(list_url, headers=head, allow_redirects=False)
            r = r.text
            # print(r)
            html = BeautifulSoup(r)
            # print(html)
            h1 = html.find('h1').text
            t = html.find(attrs={'class': 'HoverTitle'})['data-hover-title']
            print('标题：')
            print(h1)
            content = html.find(attrs={'class': 'RichText PostIndex-content av-paddingSide av-card'})
            content = content.text
            print('时间：')
            print(t)
            print('内容：')
            print(content)
        else:
            # RichContent-inner
            r = session.get(list_url, headers=head, allow_redirects=False)
            r = r.text
            # print(r)
            html = BeautifulSoup(r)

            title = html.find('h1').text
            print('标题：')
            print(title)
            times = html.find_all(attrs={'class': 'ContentItem-time'})
            for t in times:
                current = t.text
                print('时间：')
                print(current)

            inners = html.find_all(attrs={'class': 'RichContent-inner'})
            for inner in inners:
                txt = inner.text
                print('内容：')
                print(txt)
        print('-------')
    return 0


# 网址补全
def get_full_website(web, domain):
    if 'http' in web:
        return web
    else:
        return domain + web


if __name__ == '__main__':
    if isLogin():
        print('您已经登录')
        get_answer('沪东中华')
    else:
        account = input('请输入你的用户名\n>  ')
        secret = input("请输入你的密码\n>  ")
        login(secret, account)

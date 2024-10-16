---
title: "爬虫技巧"
subtitle: ""
date: 2024-09-18T00:01:03+08:00
lastmod: 2024-09-18T00:01:03+08:00
draft: false
author: "hxy"
authorLink: ""
license: ""
tags: ["技巧"]
categories: ["技巧"]
featuredImage: ""
featuredImagePreview: ""
summary: ""
hiddenFromHomePage: false
hiddenFromSearch: false
toc:
  enable: true
  auto: true
mapbox:
share:
  enable: true
comment:
  enable: true
---

# 爬虫技巧

## 抓包

- F12查看网络请求，复制cURL(Bash)
- 点击[爬虫代码生成器](https://curlconverter.com/)，生成多种变成语言爬虫代码

### 示例
```python
headers = {
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.42',
}

params = {
    'tn': 'resultjson_com',
    'word': query,
    'pn': pageNum
}

response = requests.get('https://image.baidu.com/search/acjson', params=params, headers=headers).json()
info = response['data']
parsed_info = parse_info(info)
for url in parsed_info:
    save_image(url['url'])
```
## Bs解析
- 直接requests.get({url})，加上headers伪装
- 用bs4.BeautifulSoup解析，提取各个标签及其文本
### 问题
1. 无法获取到具体数据
- 可能需要登录，尝试js逆向。
- 可采用selenium模拟浏览器点击请求，极大概率可行。
### 示例
```python
def parse_single_html(html):
    soup = BeautifulSoup(html,'html.parser')
    article_items = (soup.find("div", class_="article").find("ol",class_="grid_view").find_all("div", class_="item"))
    data_list = []
    for article_item in article_items:
        rank = article_item.find("div",class_="pic").find("em").get_text()
        info = article_item.find("div",class_="info")
        title = info.find("div",class_="hd").find("span",class_="title").get_text()
        stars = (info.find("div",class_="bd").find("div",class_="star").find_all("span"))
        rating_star = stars[0]["class"][0]
        rating_num = stars[1].get_text()
        comments = stars[3].get_text()
     
        data_list.append({
            "rank": rank,
            "title": title,
            "rating_star": rating_star.replace("rating", "").replace("-t", ""),
            "rating_num": rating_num,
            "comments": comments.replace("人评价", "")
        })
    return data_list
```


## js逆向
js逆向法主要用于需要模拟登录的场景，登录接口做了加密。
方法步骤
- F12抓包，获取登录请求 
- 若有加密，查看网站源代码
- 用execjs库运行或python重写js代码，模拟效果
- 成功登录

### 示例
```javascript
with open('../security.js') as f:
  js_data = f.read()
    ctx = execjs.compile(js_data)
encryped_pwd = ctx.call('getEncrypedPwd', public_exponent, modulus, password)
```

### 技巧
- 使用requests.session代替request发送请求，自动更新cookies，避免手动更新
- 适当修改js，明确入口函数便于py执行

## 破解滑块验证码
- 要想破解滑块验证码，需要首先获取缺口和原图的url，爬取后利用opencv进行模版匹配。
- 要求模板匹配算法进行优化，具有较高鲁棒性。
- 用selenium模拟手动拖动滑块过程

### 示例
```python
options = Options()
options.add_argument('--headless')
driver = webdriver.Firefox()
driver.get('xxxx.html') # 用selenium登录网址
slider = driver.find_element('class name', 'zfdun_slider_bar_btn')
# 找到滑块背景图片，以获取滑块的位置信息
slider_bg = driver.find_element('class name', 'zfdun_bgimg_jigsaw')
large_bg = driver.find_element('class name', 'zfdun_bgimg_img')
template_img_url = large_bg.get_attribute('src')
img_url = slider_bg.get_attribute('src')
# 获取当前页面的所有 Cookie
cookies = driver.get_cookies()
cookies = {cookie['name']: cookie['value'] for cookie in cookies}
template_res = requests.get(template_img_url, cookies=cookies)
img_res = requests.get(img_url, cookies=cookies)
# 将二进制数据转化为 numpy 数组
template_img_array = np.frombuffer(template_res.content, np.uint8)
# 使用 OpenCV 解码图片
template = cv2.imdecode(template_img_array, cv2.IMREAD_COLOR)
# 将二进制数据转化为 numpy 数组
img_array = np.frombuffer(img_res.content, np.uint8)
# 使用 OpenCV 解码图片
img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
# 计算左边距
left_margin = calculate_left_margin(template, img)
print("left_margin", left_margin)
# 输入用户名
username_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'yhm')))
username_input.send_keys(username)
# 输入密码
password_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'mm')))
password_input.send_keys(password)
# 获取滑块的初始位置和大小
slider_width = slider.size['width']
slider_start = slider.location['x']
print(slider_width)
print(large_bg.size['width'])
# 模拟拖动滑块的操作
ActionChains(driver).click_and_hold(slider).perform()
ActionChains(driver).move_by_offset(left_margin, 0).perform()
time.sleep(0.5)  # 可以根据实际情况调整等待时间
ActionChains(driver).release().perform()
# 登录按钮点击
login_button = driver.find_element('id', 'dl')
login_button.click()
cookies = driver.get_cookies()
cookies = {cookie['name']: cookie['value'] for cookie in cookies}
print("cookies:", cookies)
with open('cookies.json', 'w') as f:
    json.dump(cookies, f)
driver.quit()
```
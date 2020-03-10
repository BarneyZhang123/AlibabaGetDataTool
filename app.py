# coding=utf-8
import requests
from flask import request
from flask import Flask
from flask_cors import CORS
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app, supports_credentials=True)

# 爬取页面html结构
def get_html(url):
    headers = {
        'User-Agent':'Mozilla/5.0(Macintosh; Intel Mac OS X 10_11_4)\
        AppleWebKit/537.36(KHTML, like Gecko) Chrome/52 .0.2743. 116 Safari/537.36'

    }     #模拟浏览器访问
    response = requests.get(url,headers = headers)       #请求访问网站
    html = response.text       #获取网页源码
    return html                #返回网页源码

# 爬取商品时根据分页拼接url
def get_getCommodityList_url(url,page):
    urlArray = url.split('/')
    pageUrl = urlArray[3][-2:]
    if (pageUrl.find('-') == -1):
        urlArray[3] = urlArray[3] + '-' + str(page)
    else:
        urlArray[3] = urlArray[3][:-2] + '-' + str(page)
    _url = '/'.join(urlArray)
    return _url

#   获取产品类别
@app.route('/getProductCategories', methods=['GET','POST'])
def getData():
    url = request.args.get("url")
    menu = []
    if url:
        soup = BeautifulSoup(get_html(url + '/productlist.html'), 'lxml')   #初始化BeautifulSoup库,并设置解析器
        for li in soup.find_all(attrs={"class": "next-menu ver group-menu"}):         #遍历父节点
                for a in li.find_all(name='a'):     #遍历子节点
                    if a.string==None:
                        pass
                    else:
                        menu.append({'text':a.string,'href':url + a['href']})
        return {'code':0,'msg':menu}
    else:
        return {'code':50001,'msg':'地址出错'}

#   获取商品列表
@app.route('/getCommodityList')
def getCommodityList():
    page = 1
    maxPage = 1
    mainJson = []
    url = request.args.get("url")
    if url:
        _url = get_getCommodityList_url(url, page)
        soup = BeautifulSoup(get_html(_url), 'lxml')   #初始化BeautifulSoup库,并设置解析器
        #   爬取翻页按钮 写入总页数
        for nextBtn in soup.find_all(attrs={"class": "next-pagination-pages"}):
            _page = nextBtn.find_all(attrs={"class": "next-btn next-btn-normal next-btn-medium next-pagination-item"})[-1].string
            if _page !=None:
                maxPage = int(_page)
            print('总页数')
            print(_page)
        getJson = getList(url, page, maxPage, mainJson)
        return {'code':0,'msg':getJson}
    else:
        return {'code':50001,'msg':'地址出错'}

#   递归爬取所有商品
def getList(url, page, maxPage, mainJson):
    if url:
        _url = get_getCommodityList_url(url,page)
        soup = BeautifulSoup(get_html(_url), 'lxml')   #初始化BeautifulSoup库,并设置解析器
        #   爬取列表数据
        forIndex = 0    #便利索引
        box = soup.find(attrs={"class": "component-product-list"})                           #   父节点
        listArray = box.find_all(attrs={"class": ["icbu-product-card vertical large product-item","icbu-product-card vertical large product-item last"]})  #   所有子节点
        for item in listArray:
           a = item.find(attrs={"class": "title-con"})
           if a.string != None:
                mainJson.append({'text':a.string})
           forIndex += 1
           if forIndex == len(listArray):               #   当前周期遍历完毕
                print('第' + str(page) + '页循环结束')
                print(len(mainJson))
                if page != maxPage:                     #   如果不是最后一页则递归遍历 直到所有数据爬取完毕
                    return getList(url, page + 1, maxPage, mainJson)
                else:
                    return mainJson
    else:
        return mainJson

if __name__ == "__main__":
    app.run(
    host = '0.0.0.0',#任何ip都可以访问
    port = 5000,#端口
    debug = True
)

# coding=utf-8

import re
import requests
from pyquery import PyQuery as Pq


class BaiduSearchSpider(object):
    def __init__(self, searchText, page):
        self.url = "http://www.baidu.com/baidu?wd=%s&pn=%d&tn=monline_4_dg" %(searchText,page)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/600.5.17 (KHTML, like Gecko) Version/8.0.5 Safari/600.5.17"}
        self._page = None

    @property
    def page(self):
        if not self._page:
            r = requests.get(self.url, headers=self.headers)
            r.encoding = 'utf-8'
            self._page = Pq(r.text)
        return self._page

    @property
    def baiduURLs(self):
        return [(site.attr('href'), site.text().encode('utf-8')) for site in
                self.page('div.result.c-container  h3.t  a').items()]

    @property
    def originalURLs(self):
        tmpURLs = self.baiduURLs
        originalURLs = []
        for tmpurl in tmpURLs:
            tmpPage = requests.get(tmpurl[0], allow_redirects=False)
            if tmpPage.status_code == 200:
                urlMatch = re.search(r'URL=\'(.*?)\'', tmpPage.text.encode('utf-8'), re.S)
                originalURLs.append((urlMatch.group(1), tmpurl[1]))
            elif tmpPage.status_code == 302:
                originalURLs.append((tmpPage.headers.get('location'), tmpurl[1]))
            else:
                print('No URL found!!')

        return originalURLs

def main():
    searchText = input("搜索内容是：")
    page = input("搜索页数：")
    page = int(page)

    with open('%s.csv'%searchText, 'w') as f:
        f.write(searchText + '\n')
        for p in range(0,page*10,10):
            print('page %d'%(p/10+1))
            bdsearch = BaiduSearchSpider(searchText, p)
            originalurls = bdsearch.originalURLs
            print(len(originalurls))
            for u in originalurls:
                f.write(u[0] + '\n')

if __name__ == '__main__':
    main()



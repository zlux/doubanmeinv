# -*- coding: utf-8 -*-
import scrapy
import re
from doubanmeinv.items import dbmeinvItem,UserItem
import json
import time
from datetime import datetime
from scrapy.exceptions import CloseSpider

import sys
reload(sys)
sys.setdefaultencoding('utf8')

class DbmeinvSpider(scrapy.Spider):
    name = "dbMeinv"
    allowed_domains = ["www.dbmeinv.com"]
    start_urls = (
        'http://www.dbmeinv.com/dbgroup/rank.htm?pager_offset=1',
    )
    baseUrl = 'http://www.dbmeinv.com'
    close_down = False

    def parse(self, response):
        request = scrapy.Request(response.url,callback=self.parsePageContent)
        yield request

    #解析每一页的列表
    def parsePageContent(self, response):
        for sel in response.xpath('//div[@id="main"]//li[@class="span3"]'):
            item = dbmeinvItem()
            title = sel.xpath('.//div[@class="bottombar"]//a[1]/text()').extract()[0]
            #用strip()方法过滤开头的\r\n\t和空格符
            item['title'] = title.strip()
            item['thumbUrl'] = sel.xpath('.//div[@class="img_single"]//img/@src').extract()[0]
            href = sel.xpath('.//div[@class="img_single"]/a/@href').extract()[0]
            item['href'] = href
            #正则解析id
            pattern = re.compile("dbgroup/(\d*)")
            res = pattern.search(href).groups()
            item['feedId'] = res[0]
            #跳转到详情页面
            request = scrapy.Request(href,callback=self.parseMeinvDetailInfo)
            request.meta['item'] = item
            yield request
        #判断是否超过限制应该停止
        if(self.close_down == True):
            print "数据重复，close spider"
            raise CloseSpider(reason = "reach max limit")
        else:
            #获取下一页并加载
            next_link = response.xpath('//div[@class="clearfix"]//li[@class="next next_page"]/a/@href')
            if(next_link):
                url = next_link.extract()[0]
                link = self.baseUrl + url
                yield scrapy.Request(link,callback=self.parsePageContent)

    #解析详情页面
    def parseMeinvDetailInfo(self, response):
        item = response.meta['item']
        description = response.xpath('//div[@class="panel-body markdown"]/p[1]/text()')
        if(description):
            item['description'] = description.extract()[0]
        else:
            item['description'] = ''
        #上传时间
        createOn = response.xpath('//div[@class="info"]/abbr/@title').extract()[0]
        format = "%Y-%m-%d %H:%M:%S.%f"
        t = datetime.strptime(createOn,format)
        timestamp = int(time.mktime(t.timetuple()))
        item['createOn'] = timestamp
        #用户信息
        user = UserItem()
        avatar = response.xpath('//div[@class="user-card"]/div[@class="pic"]/img/@src').extract()[0]
        name = response.xpath('//div[@class="user-card"]/div[@class="info"]//li[@class="name"]/text()').extract()[0]
        home = response.xpath('//div[@class="user-card"]/div[@class="opt"]/a[@target="_users"]/@href').extract()[0]
        user['avatar'] = avatar
        user['name'] = name
        #正则解析id
        pattern = re.compile("/users/(\d*)")
        res = pattern.search(home).groups()
        #user['userId'] = res[0]
        #item['userId'] = res[0]
        #将item关联user
        item['userInfo'] = user
        #解析链接
        pics = []
        links = response.xpath('//div[@class="panel-body markdown"]/div[@class="topic-figure cc"]')
        if(links):
            for a in links:
                img = a.xpath('./img/@src')
                if(img):
                    picUrl = img.extract()[0]
                    pics.append(picUrl)
        #转成json字符串保存
        item['pics'] = json.dumps(list(pics))
        yield item
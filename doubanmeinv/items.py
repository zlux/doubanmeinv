# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Field, Item

class dbmeinvItem(Item):
    feedId = Field()         #feedId
#    userId = Field()         #用户id
    createOn = Field()       #创建时间
    title = Field()          #feedTitle
    thumbUrl = Field()       #feed缩略图url
    href = Field()           #feed链接
    description = Field()    #feed简介
    pics = Field()           #feed的图片列表
    userInfo = Field()       #用户信息

class UserItem(Item):
#    userId = Field()         #用户id
    name = Field()           #用户name
    avatar = Field()         #用户头像

# -*- coding: utf-8 -*-
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
import json

class ImageCachePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        pics = item['pics']
        list = json.loads(pics)
        for image_url in list:
            yield Request(image_url)

    def item_completed(self, results, item, info):
        image_paths=[x['path'] for ok,x in results if ok]
        if not image_paths:
            print "图片未下载好:%s" % image_paths
            raise DropItem('图片未下载好 %s'%image_paths)

# -*- coding: utf-8 -*-
import scrapy
import socket
import datetime

from scrapy.http import Request
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose
from scrapy_splash import SplashRequest
from items import ArticleItem




class Apaspider(scrapy.Spider):
    name = 'apaorg'
    allowed_domains = ["apa.org"]
    start_urls = [
        "https://www.apa.org/pubs/journals/rmh/",
        "https://www.apa.org/pubs/journals/rmh/?tab=1",
        "https://www.apa.org/pubs/journals/rmh/?tab=2",
        "https://www.apa.org/pubs/journals/rmh/?tab=3",
        "https://www.apa.org/pubs/journals/rmh/?tab=4",
        "https://www.apa.org/pubs/journals/rmh/?tab=5"
    ]

    custom_settings = {
        'FILES_STORE': 'output/files',
        'IMAGES_STORE': 'output/images',
        'FEED_URI': 'output/feeds/%(name)s/%(time)s.json',
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'COOKIES_ENABLED': True,
        # 'DOWNLOAD_DELAY': 3,
        # 'CRAWLERA_ENABLED': False,
    }


    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(
                url,
                headers={
                    'X-Crawlera-Session': 'create',
                    'X-Crawlera-profile': 'desktop',
                    'X-Crawlera-cookies': 'disable',
                },
                callback=self.restart_requests,
                meta={'url': url}
            )

    
    def restart_requests(self, response):
        url = response.meta['url']

        session_id = response.headers.get('X-Crawlera-Session', '')

        
        yield SplashRequest(url, self.parse_list, 
                            cookies={'store_language':'en'},
                            endpoint='execute', 
                            args = {'wait':30 })
    
    def parse_list(self, response):
        
        print(response.url)
        print(response.text)
        
        l = ItemLoader(item=ArticleItem(), response=response)
        
        if "tab" in response.url:
            
            body  = response.xpath('//section[@class="rwdTabWidgetDetail resp-tab-content resp-tab-content-active"]').css('wysiwyg lengthy"').css('p::text').extract()
                                    
        else:
            
            for f in response.xpath('//*[@id="announcements"]'):
            
                d = f.css('a::text').extract()
            
                e = f.css('a::attr(href)').extract()
            
                for i in range(0,len(e)):
                
                    if '://' not in e[i]:
                    
                        link = "https://www.apa.org" + e[i]
                
                    
                    title = d[i]
                                    
                    yield scrapy.Request(
                        link,
                        headers={
                            'X-Crawlera-Session': session_id,
                            'X-Crawlera-profile': 'desktop',
                            'X-Crawlera-cookies': 'disable',
                        },
                        callback=self.restart_requests
                    )
                        

                l.add_value('title',title)
                
                l.add_value('body',body)
            
                l.add_value('file_urls',link)
            
                l.add_value('project', self.settings.get('BOT_NAME'))
            
                l.add_value('spider', self.name)
            
                l.add_value('server', socket.gethostname())
            
                l.add_value('date', datetime.datetime.utcnow())

                yield l.load_item()       

            

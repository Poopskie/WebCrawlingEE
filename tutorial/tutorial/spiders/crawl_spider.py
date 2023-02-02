import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


global found, sites_crawled
found = ['https://www.goodreads.com']
sites_crawled = 0

class BFSSpider(CrawlSpider):
    name = 'BFSspider'
    allowed_domains = ['goodreads.com']
    #start_urls = ['https://en.wikipedia.org/wiki/Cat']


    def start_requests(self):
        yield scrapy.Request('https://www.goodreads.com', self.parse)


    def parse(self, response):
        global found, sites_crawled
        for href in response.xpath('//a/@href').getall(): # finds all links
            if sites_crawled >= 3000:
                return

            url = response.urljoin(href)
            if url not in found: # eliminates duplicates
                found.append(url)
                sites_crawled += 1
                yield {"url": response.urljoin(href), "sitenumber": sites_crawled} # prints into JSON
                yield scrapy.Request(response.urljoin(href), self.parse) # Recursion
            
            
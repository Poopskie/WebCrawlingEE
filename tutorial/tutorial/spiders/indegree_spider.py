import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class frontier_url():
    def __init__(self, url, count, flag):
        self.url = url
        self.count = count
        self.flag = flag

    def add_count(self):
        self.count += 1

    def visited(self):
        self.flag = True

global frontier, found, sites_crawled
frontier = []
found = ['https://www.goodreads.com/ ']
sites_crawled = 0


class IndegreeSpider(scrapy.Spider):
    name = 'indegree'
    allowed_domains = ['goodreads.com']
    #start_urls = ['https://en.wikipedia.org/wiki/Cat']


    def start_requests(self):
        yield scrapy.Request('https://www.goodreads.com/ ', self.parse)

    def parse(self, response):
        global frontier, found, sites_crawled
        for href in response.xpath('//a/@href').getall(): # finds all links
            if sites_crawled >= 3000:
                return

            url = response.urljoin(href)

            if url not in found: # add new url to frontier
                found.append(url)
                item = frontier_url(url, 1, False)
                frontier.append(item)
            else:
                for i in range(len(frontier)): # if existing, then add to count
                    if frontier[i].url == url:
                        frontier[i].add_count()
            
            # sort list by decending count
            frontier.sort(reverse=True, key=lambda x:x.count)

            for i in range(len(frontier)):
                if not frontier[i].flag: # if haven't been checked
                    frontier[i].visited() # flips flag
                    sites_crawled += 1
                    yield {"url": url, "sitenumber": sites_crawled} # prints into JSON
                    yield scrapy.Request(frontier[i].url, self.parse)
                    break # ends instance



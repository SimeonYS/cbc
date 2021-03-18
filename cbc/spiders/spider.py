import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import CbcItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'
base = 'https://cbc.prezly.com/?offset={}&limit=4&layout=plain&xhr=1'
class CbcSpider(scrapy.Spider):
	name = 'cbc'
	offset = 0
	start_urls = [base.format(offset)]

	def parse(self, response):
		post_links = response.xpath('///a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		if len(post_links) == 5:
			self.offset += 5
		elif len(post_links)==4:
			self.offset +=4
		yield response.follow(base.format(self.offset),self.parse)

	def parse_post(self, response):
		date = response.xpath('//span[contains(@class,"story-date")]/text()').get()
		date = re.findall(r'\d+\s\w+\s\d+',date)
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="story__column story__column--content"]//text()[not (ancestor::h1 or ancestor::p[@class="story-intro"])]').getall() + response.xpath('//section[@class="story__content"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=CbcItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()

import scrapy
import json

class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    start_urls = ['http://quotes.toscrape.com']

    def parse(self, response):
        quotes = []
        authors = []

        for quote in response.css('div.quote'):
            quote_data = {
                'text': quote.css('span.text::text').get(),
                'author': quote.css('span small::text').get(),
                'tags': quote.css('div.tags a.tag::text').getall(),
            }
            quotes.append(quote_data)

            author_link = quote.css('span small a::attr(href)').get()
            if author_link:
                yield response.follow(author_link, self.parse_author)

        next_page = response.css('li.next a::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

        yield {
            'quotes': quotes,
        }

    def parse_author(self, response):
        author_name = response.css('h3.author-title::text').get()
        born_date = response.css('span.author-born-date::text').get()
        born_location = response.css('span.author-born-location::text').get()
        description = response.css('div.author-description::text').get()

        author_data = {
            'fullname': author_name,
            'born_date': born_date,
            'born_location': born_location,
            'description': description.strip() if description else '',
        }

        yield {
            'authors': [author_data],
        }

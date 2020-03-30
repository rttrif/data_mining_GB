# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Response


class HabrSpider(scrapy.Spider):
    name = 'habr'
    allowed_domains = ['habr.com']
    start_urls = ['https://habr.com/ru/top/weekly/']

    def parse(self, response: Response):
        for pag_page in response.css(
                '.page__footer ul.toggle-menu_pagination li.toggle-menu__item_pagination a::attr("href")'):
            yield response.follow(pag_page, callback=self.parse)

        for post_url in response.css('ul.content-list_posts article.post h2.post__title a::attr("href")'):
            yield response.follow(post_url, callback=self.post_parse)

    def post_parse(self, response: Response):
        item = {
            'url': response.url,
            'writer': {'nicname': response.css(
                'article.post header.post__meta a.post__user-info span.user-info__nickname::text').extract_first(),
                       'url': response.css(
                           'article.post header.post__meta a.post__user-info::attr("href")').extract_first()
                       },
            'pub_date': response.css(
                'article.post header.post__meta span.post__time::attr("data-time_published")').extract_first(),
            'comments_count': response.css('span.post-stats__comments-count::text').extract_first(),
            'comment_autors': [{'name': itm.xpath('@data-user-login').get(),
                                'url': itm.xpath('@href').get()} for itm in
                               response.css('ul#comments-list .comment__head a.user-info')
                               ]
        }
        yield item

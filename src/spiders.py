import scrapy
import re
import os.path


class Spider(scrapy.Spider):
    def __init__(self, name, url, href_xpath_rules, href_regex, articles_list):
        self.name = name
        self.url = url
        self.href_xpath_rules = href_xpath_rules
        self.href_regex = href_regex
        self.articles_list = articles_list

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response, **kwargs):
        page = re.search(r"https://[.a-z]*", response.url).group()

        contained_hrefs = ' '.join(response.xpath(self.href_xpath_rules).getall())

        for regex in self.href_regex:
            r = re.compile(regex)
            contained_hrefs = r.findall(contained_hrefs)

            # needed for cnn crawling in order to get articleList as a list, not a list inside a list
            if self.name == "cnn" and len(contained_hrefs) == 1:
                contained_hrefs = contained_hrefs[0]

        for link in set(contained_hrefs):
            link = page + link
            yield scrapy.Request(url=link, callback=self.download_article)

    def download_article(self, response):
        title = response.css('title::text').get()
        filename = os.path.join(os.path.pardir, "articles", self.name, title + ".html")

        with open(filename, 'wb') as f:
            f.write(response.body)

        self.articles_list.append((filename, response.request.url))

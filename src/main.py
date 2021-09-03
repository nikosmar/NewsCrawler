import spiders
import data_preprocessor
import inverted_index
import json
import os.path
from scrapy.crawler import CrawlerProcess


if __name__ == "__main__":
    new_articles = []

    with open(os.path.join(os.path.pardir, "news_websites.json"), 'r') as json_input:
        sites_json = json.load(json_input)

    process = CrawlerProcess()

    # load the needed parameters from the json file
    # and create a spider for each website
    for site in sites_json["sites"]:
        name = site["name"]
        url = site["url"]
        href_xpath_rules = site["href_xpath_rules"]
        href_regex = site["href_regex"]
        text_xpath_rules = '|'.join(site["text_xpath_rules"])
        new_articles.append([text_xpath_rules])

        # make sure that there exists a directory for every website
        target_directory = os.path.join(os.path.pardir, "articles", str(name))
        if not os.path.exists(target_directory):
            try:
                os.makedirs(os.path.abspath(target_directory))
            except OSError:
                print(f"Unable to create a directory for {name} articles.")
                exit(1)

        process.crawl(spiders.Spider, name=name, url=url, href_xpath_rules=href_xpath_rules, href_regex=href_regex,
                      articles_list=new_articles[-1])

    del site, sites_json, name, url, href_xpath_rules, href_regex

    process.start()

    target_directory = os.path.join(os.path.pardir, "tagged_articles")
    if not os.path.exists(target_directory):
        try:
            os.makedirs(os.path.abspath(target_directory))
        except OSError:
            print("Unable to create a directory for tagged articles.")
            exit(1)

    tagged_articles = []

    for articles in new_articles:
        text_xpath_rules = articles[0]

        for (article, _) in articles[1:]:
            tagged_article = data_preprocessor.html_to_tagged_text(article, text_xpath_rules)
            tagged_articles.append(tagged_article)

    del article, articles

    lemmatized_articles = data_preprocessor.tagged_text_vectorizer(tagged_articles)

    del tagged_articles

    inv_index = inverted_index.create(lemmatized_articles, new_articles)
    inverted_index.store_to_file(inv_index)

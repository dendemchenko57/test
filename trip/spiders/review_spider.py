import scrapy

from scrapy_splash import SplashRequest
from selenium import webdriver

from trip.items import ReviewItem
from trip.proxy import GimmeProxy

# options to work selenium without GUI
options = webdriver.ChromeOptions()
options.add_argument("headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")


class TripAdvisorReview(scrapy.Spider):
    name = "tripadvisor_review"

    start_urls = [
        "https://www.tripadvisor.com.sg/Hotel_Review-g293916-d301388-Reviews-Montien_Hotel_Bangkok-Bangkok.html"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.proxy_suplier = GimmeProxy()
        self.driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver", chrome_options=options)

    def start_requests(self):
        for url in self.start_urls:
            # SplashRequest need to load whole page before scraping
            yield SplashRequest(url=url, callback=self.parse_review_page,
                                args={'wait': 3})

    def parse_review_page(self, response):
        # get review item from review list page
        review_page = response.xpath(
            "//div[@class[contains(.,'hotels-review-list-parts-ReviewTitle__reviewTitle')]]/a/@href").extract()
        author_names = response.xpath(
            "//a[@class[contains(.,'ui_header_link social-member-event-MemberEventOnObjectBlock__member')]]/text()").extract()[:5]
        author_locations = response.xpath(
            "//span[@class[contains(.,'default social-member-common-MemberHometown__hometown')]]/text()").extract()[:5]
        author_contributions_and_votes = response.xpath(
            "//span[@class[contains(.,'social-member-MemberHeaderStats__bold')]]/text()").extract()[:10]
        posted_at_list = response.xpath(
            "//div[@class[contains(.,'ocial-member-event-MemberEventOnObjectBlock__event_type')]]/span/text()").extract()[:5]

        if review_page:
            # going to all review_pages
            for i in range(len(review_page)):
                url = response.urljoin(review_page[i])
                author_name = author_names[i]
                author_location = author_locations[i]
                author_contribution = author_contributions_and_votes[0::2][i]
                author_vote = author_contributions_and_votes[1::2][i]
                posted_at = posted_at_list[:5][i]
                # add proxy to a request
                proxy = self.proxy_suplier.receive_proxy()
                yield SplashRequest(url, self.parse_review,
                                    args={'wait': 4, 'proxy': proxy},
                                    meta={'author_name': author_name,
                                          'author_location': author_location,
                                          'author_contribution': author_contribution,
                                          'author_vote': author_vote,
                                          'posted_at': posted_at})
        next_page = response.xpath('//a[@class="ui_button nav next primary "]/@href').extract()
        if next_page:
            url = response.urljoin(next_page[-1])
            yield SplashRequest(url, self.parse_review_page, args={'wait': 4})

    def parse_review(self, response):
        from time import sleep
        item = ReviewItem()
        title = response.xpath(".//h1[@id='HEADING']/text()").get()
        date_of_stay = response.xpath(
            "//div[@class[contains(.,'prw_rup prw_reviews_stay_date_hsx')]]/text()").get()
        review = response.xpath("//span[@class[contains(.,'fullText ')]]/text()").get()
        author_rating = response.xpath(
            "//span[@class[contains(.,'ui_bubble_rating')]]/@class").re(
            r'bubble_(\d+)')[0]
        item['author_name'] = response.meta['author_name']
        item['author_location'] = response.meta['author_location']
        item['author_contributions'] = response.meta['author_contribution']
        item['helpful_votes'] = response.meta['author_vote']
        item['posted_at'] = response.meta['posted_at']
        if not title:
            #old reviews needs to be load before it scrapes. That's why selenium is used
            self.driver.get(response.url)
            # wait till it loads
            sleep(3)
            title = self.driver.find_element_by_xpath(".//h1[@id='HEADING']").text
        if not review:
            # old reviews needs to be load before it scrapes. That's why selenium is used
            self.driver.get(response.url)
            # wait till it loads
            sleep(3)
            review = self.driver.find_element_by_xpath("//span[@class[contains(.,'fullText')]]").text
            if not review:
                review = self.driver.find_element_by_xpath("//span[@class[contains(.,'summaryText')]]").text
        item['title'] = title
        item['date_of_stay'] = date_of_stay
        item['review'] = review
        item['author_rating'] = author_rating

        yield item

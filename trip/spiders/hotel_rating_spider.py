import scrapy

from trip.items import HotelRatingItem
from scrapy_splash import SplashRequest


class TripAdvisorHotelRating(scrapy.Spider):
    name = "tripadvisor_hotel_rating"

    start_urls = [
        "https://www.tripadvisor.com/Hotel_Review-g293916-d301388-Reviews-Montien_Hotel_Bangkok-Bangkok.html"]

    allowed_domains = ["https://www.tripadvisor.com", ]

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url=url, callback=self.parse,
                                args={'wait': 1},)

    def parse(self, response):
        item = HotelRatingItem()
        ranking = response.xpath("//b[@class[contains(.,'rank')]]/text()").get()
        rating_overall = response.xpath(
            "//a[@class[contains(.,'hotels-hotel-review-about-with-photos-Reviews__bubbleRating')]]/span/@class").re(
            r'bubble_(\d+)')[0]
        reviews_count = response.xpath(
            "//span[@class[contains(.,'hotels-hotel-review-about-with-photos-Reviews__seeAllReviews')]]/text()").re(
            r'(\d+)')[0]
        locating_rating = \
            response.xpath("//*[@id='ABOUT_TAB']/div[2]/div[1]/div[2]/div[1]/div[1]/span").re(
                r'bubble_(\d+)')[0]
        cleaniness_rating = \
            response.xpath("//*[@id='ABOUT_TAB']/div[2]/div[1]/div[2]/div[2]/div[1]/span").re(
                r'bubble_(\d+)')[0]
        service_rating = \
            response.xpath("//*[@id='ABOUT_TAB']/div[2]/div[1]/div[2]/div[3]/div[1]/span").re(
                r'bubble_(\d+)')[0]
        value_rating = \
            response.xpath("//*[@id='ABOUT_TAB']/div[2]/div[1]/div[2]/div[4]/div[1]/span").re(
                r'bubble_(\d+)')[0]
        traveler_rating_five, traveler_rating_four, traveler_rating_three, traveler_rating_two, traveler_rating_one = [
            i.get() for i in response.xpath(
                "//div[@class[contains(.,'hotels-review-list-parts-ReviewFilters__filters_wrap')]]/div/div/ul/li/span[2]/text()")]
        item['ranking'] = ranking
        item['rating_overall'] = rating_overall
        item['reviews_count'] = reviews_count
        item['cleaniness_rating'] = cleaniness_rating
        item['service_rating'] = service_rating
        item['value_rating'] = value_rating
        item['locating_rating'] = locating_rating
        item['traveler_rating_five'] = traveler_rating_five
        item['traveler_rating_four'] = traveler_rating_four
        item['traveler_rating_three'] = traveler_rating_three
        item['traveler_rating_two'] = traveler_rating_two
        item['traveler_rating_one'] = traveler_rating_one
        yield item

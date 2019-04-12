# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ReviewItem(scrapy.Item):
    # define the fields for your item here like:
    author_name = scrapy.Field()
    author_location = scrapy.Field()
    date_of_stay = scrapy.Field()
    author_rating = scrapy.Field()
    author_contributions = scrapy.Field()
    helpful_votes = scrapy.Field()
    posted_at = scrapy.Field() #date
    review = scrapy.Field()
    title = scrapy.Field()


class HotelItem(scrapy.Item):
    name = scrapy.Field()
    address = scrapy.Field()
    city = scrapy.Field()
    neighbourhood = scrapy.Field()
    hotel_description = scrapy.Field()
    url_tripadvisor = scrapy.Field()
    url_agoda = scrapy.Field() # ?
    room_count = scrapy.Field()
    hotel_class = scrapy.Field()
    hotel_style = scrapy.Field()
    getting_there = scrapy.Field()


class HotelRatingItem(scrapy.Item):
    added_at = scrapy.Field()
    ranking = scrapy.Field()  #447 of 995 Hotels in Bangkok
    rating_overall = scrapy.Field()
    reviews_count = scrapy.Field()
    locating_rating = scrapy.Field()
    cleaniness_rating = scrapy.Field()
    service_rating = scrapy.Field()
    value_rating = scrapy.Field()
    traveler_rating_five = scrapy.Field() #float
    traveler_rating_four = scrapy.Field() #float
    traveler_rating_three = scrapy.Field() #float
    traveler_rating_two = scrapy.Field() #float
    traveler_rating_one = scrapy.Field() #float




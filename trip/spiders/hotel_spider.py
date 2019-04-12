import scrapy

from scrapy_splash import SplashRequest
from selenium import webdriver
from time import sleep

from trip.items import HotelItem

# options to work selenium without GUI
options = webdriver.ChromeOptions()
options.add_argument("headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")


class TripAdvisorHotelItem(scrapy.Spider):
    name = "tripadvisor_hotel"

    start_urls = [
        "https://www.tripadvisor.com/Hotel_Review-g293916-d301388-Reviews-Montien_Hotel_Bangkok-Bangkok.html"]

    allowed_domains = ["https://www.tripadvisor.com", ]

    def __init__(self):
        self.driver = webdriver.Chrome(chrome_options=options)

    def start_requests(self):
        for url in self.start_urls:
            # SplashRequest need to load whole page before scraping
            yield SplashRequest(url=url, callback=self.parse,
                                args={'wait': 3},)

    def parse(self, response):
        # In future parse start page with all hotels in the city
        header = response.xpath(
            '//div[@class="ui_columns is-multiline is-mobile contentWrapper"]')
        title_container = header.xpath(
            ".//div[@class='ui_column is-12-tablet is-10-mobile hotelDescription']")
        hotel_title = title_container.xpath(
            ".//h1[@id='HEADING']/text()").get()
        hotel_street = response.xpath(
            "//span[@class[contains(.,'street-address')]]/text()").get()
        hotel_city = response.xpath(
            "//span[@class[contains(.,'locality')]]/text()").get()
        # get url to selenium
        self.driver.get(response.url)
        # wait till it loads
        sleep(3)
        next = self.driver.find_element_by_xpath("//div[@data-vendorname[contains(.,'Agoda')]]")
        if next:
            # click on agora url
            next.click()
            # wait till redirect ends loads
            sleep(2)
            # switching to agoda tab
            self.driver.switch_to.window(self.driver.window_handles[1])
            agoda_url = self.driver.current_url
        else:
            agoda_url = "Not provided"

        hotel_country = response.xpath(
            "//span[@class[contains(.,'country-name')]]/text()").get()
        address = hotel_street + hotel_city + hotel_country
        neighbourhood = response.xpath(
            "//div[@class[contains(.,'Neighborhood__name')]]/text()").get()
        hotel_description = response.xpath(
            "//div[@class[contains(.,'common-text-ReadMore__content')]]/text()").get()
        url_tripadvisor = response.url
        additional_info = response.xpath(
            "//div[@class[contains(.,'hotels-hotel-review-about-addendum-AddendumItem__item')]]")
        room_count = [i.xpath(
            ".//div[@class='hotels-hotel-review-about-addendum-AddendumItem__content--iVts5']/text()").get()
                      for i in additional_info if i.xpath(
                ".//div[@class='hotels-hotel-review-about-addendum-AddendumItem__title--2QuyD']/text()").get() == 'NUMBER OF ROOMS'][0]
        hotel_class = response.xpath(
            "//span[@class[contains(.,'ui_star_rating')]]/@class").re(
            r'star_(\d+)')[0]
        hotel_style = [i.xpath(
            "//div[@class[contains(.,'hotels-hotel-review-about-with-photos-layout-TextItem__textitem')]]/text()").get()
                       for i in response.xpath(
                "//div[@class[contains(.,'ui_column is-6')]]") if i.xpath(
                "//div[@class[contains(.,'hotels-hotel-review-about-with-photos-layout-Subsection__title')]]/text()").get() == 'HOTEL STYLE'][0]
        #all getting there places
        all_places = [b.get() for b in response.xpath(
            "//span[@class[contains(., 'hotels-hotel-review-location-NearbyTransport__name')]]/text()")]
        # all getting there icons to places
        all_icons_to_places = [b.re(r'flights|train')[0] for b in response.xpath(
            "//span[@class[contains(., 'hotels-hotel-review-location-NearbyTransport__typeIcon')]]/@class")]
        # all getting there info to places
        activities = [b.re(r'parking|activities')[0] for b in response.xpath(
            "//span[@class[contains(., 'hotels-hotel-review-location-NearbyTransport__travelIcon')]]")]
        # all getting there time
        lenght_time = [i.get() for i in response.xpath(
            "//span[@class[contains(.,'hotels-hotel-review-location-NearbyTransport__travelIcon')]]/following-sibling::span/span/text()")]
        # block to connect all getting there info to one hotel
        lenght_and_time_pairs = list()
        while (lenght_time):
            a = lenght_time.pop(0)
            b = lenght_time.pop(0)
            lenght_and_time_pairs.append((a, b))
        getting_there = list(
            zip(all_places, ["airport" if i == 'flights' else i for i in all_icons_to_places],
                ["car" if i == 'parking' else "by walk" for i in activities],
                lenght_and_time_pairs))

        hotel_item = HotelItem()
        hotel_item['name'] = hotel_title
        hotel_item['address'] = address
        hotel_item['city'] = hotel_city
        hotel_item['neighbourhood'] = neighbourhood
        hotel_item['hotel_description'] = hotel_description
        hotel_item['url_tripadvisor'] = url_tripadvisor
        hotel_item['room_count'] = room_count
        hotel_item['hotel_class'] = hotel_class
        hotel_item['hotel_style'] = hotel_style
        hotel_item['getting_there'] = getting_there
        hotel_item['url_agoda'] = agoda_url

        yield hotel_item

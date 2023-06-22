import json
import re

import scrapy

from helper import price_format, remove_unicode_char, extract_number_only


class SuchenMobileDe(scrapy.Spider):
    def __init__(self, urls, img_idx, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = urls
        self.img_idx = img_idx

    name = 'suchen_mobile_de'
    allowed_domains = ["suchen.mobile.de"]

    def parse(self, response, **kwargs):
        car_maker_path = response.xpath('//script[contains(.,"mobile.dart.setAdData")]').get()
        car_maker_json = json.loads(re.search('mobile\.dart\.setAdData\(.*?(.*?)\); } mobile\.adv\.adSlots',
                                              car_maker_path).group(1))

        ad_title = car_maker_json['adSpecificsMakeModel']

        manufacturer_brand = car_maker_json['adSpecificsMake']
        model = car_maker_json['ad']['specifics']['model']

        ad_id = car_maker_json['adId']
        car_id = f"{ad_id}_{ad_title}".replace(' ', "_").lower().replace("-", '_')

        car_price = car_maker_json['adPrice']

        car_images = response.xpath('//div[@class="image-gallery"]//img/@data-overlay-src').getall()
        selected_images = [car_images[int(i) - 1] for i in self.img_idx]

        mileage = remove_unicode_char(response.xpath('//div[@id="mileage-v"]//text()').get())
        transmission = response.xpath('//div[@id="transmission-v"]//text()').get()
        numberofpreviousowners = response.xpath('//div[@id="numberOfPreviousOwners-v"]//text()').get()
        fuel = response.xpath('//div[@id="fuel-v"]/text()').get()

        firstregistration = response.xpath('//div[@id="firstRegistration-v"]//text()').get()
        if firstregistration:
            firstregistration = firstregistration.replace('/', '.')

        power = response.xpath('//div[@id="power-v"]//text()').get()
        if power:
            power = '/'.join(extract_number_only(remove_unicode_char(power)))
        color = response.xpath('//div[@id="color-v"]//text()').get()

        car_features = response.xpath('//div[@id="features"]//div/p/text()').getall()

        yield {
            "ad_id": ad_id,
            'car_id': car_id,
            'ad_title': ad_title,
            'manufacturer_brand': manufacturer_brand,
            "model": model,
            "car_features": car_features,
            'car_images': selected_images,
            'car_price': car_price,
            'car_specifications': [
            ['Herstellermarke:', manufacturer_brand],
            ['Fahrzeugtyp:', model],
            ['Laufleistung (km):', mileage],
            ['Motorart:', fuel],
            ['Getriebeart:', transmission],
            ['Leistung KW/PS:', power],
            ['Lackierung:', color],
            ['Erstzulassung:', firstregistration],
            ['Anzahl Vorbesitzer:', numberofpreviousowners],
        ]
        }

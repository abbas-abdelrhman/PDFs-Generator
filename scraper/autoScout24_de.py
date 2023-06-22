import json
import re

import scrapy

from helper import price_format, remove_unicode_char, extract_number_only


class AutoScout24De(scrapy.Spider):
    def __init__(self, urls, img_idx, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = urls
        self.img_idx = img_idx

    name = 'autoScout24_de'
    allowed_domains = ["autoScout24.de"]

    def parse(self, response, **kwargs):
        car_maker_path =  response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
        car_maker_json = json.loads(car_maker_path)['props']['pageProps']['listingDetails']

        manufacturer_brand = car_maker_json['vehicle']['make']
        model = car_maker_json['vehicle']['model']

        ad_id = car_maker_json['id']
        car_id = f'{ad_id}_{manufacturer_brand}_{model.replace(" ","_")}'

        car_price = car_maker_json['prices']['public']['priceRaw']

        car_images = car_maker_json['images']
        selected_images = [car_images[int(i) - 1] for i in self.img_idx]

        mileage = car_maker_json['vehicle']['mileageInKm']

        transmission = car_maker_json['vehicle']['transmissionType']

        numberofpreviousowners = ''

        fuel = car_maker_json['vehicle']['fuelCategory']['formatted']

        firstregistration = car_maker_json['vehicle']['firstRegistrationDate']
        if firstregistration:
            firstregistration = firstregistration.replace('/', '.')

        power = f"{car_maker_json['vehicle']['rawPowerInKw']}/{car_maker_json['vehicle']['rawPowerInHp']}"

        color = car_maker_json['vehicle']['bodyColor']

        # car_features = car_maker_json['description']
        # car_features = re.findall('<li>(.*?)<br',car_features)
        # # if car_features:
        # regex = re.compile(r'<strong>')
        # filtered_car_features = [i for i in car_features if not regex.match(i)]
        # else:

        car_features = response.xpath('//div[@class="ExpandableDetailsSection_childContainer__jxRWN ExpandableDetailsSection_childContainer_collapsed__MVauK"]//li//text()').getall()

        yield {
            'car_id': car_id,
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

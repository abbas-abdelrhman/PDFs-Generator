#!/usr/bin/env python3

import json
import shutil

import wget
from PIL import Image
from scrapy.crawler import CrawlerProcess

from helper import *
from pdf_generator import PdfGenerator
from scraper.autoScout24_de import AutoScout24De
from scraper.suchen_mobile_de import SuchenMobileDe


def calling_spider(spider_name, url, img_idx):
    process = CrawlerProcess(
        settings={
            "FEEDS": {
                "api/item.json": {
                    "format": "json",
                    "overwrite": True,
                }
            },
        }
    )
    process.crawl(spider_name, url, img_idx)
    process.start()


def read_car_data():
    with open('api/item.json') as data:
        return json.loads(data.read())[0]


def download_image(images):
    # image_folder = resource_path('images')

    if os.path.exists(f'images/'):
        shutil.rmtree(f'images/')
        os.mkdir(f'images')
    else:
        os.mkdir(f'images')

    root_path = f'images/'

    imgs = [wget.download(img, out=root_path + f"img-{idx}" + '.jpg') for idx, img in enumerate(images)]
    for img in imgs:
        format_image(img)

    # return [wget.download(img, out=root_path + f"img-{idx}" + '.jpg') for idx, img in enumerate(images)]


def format_image(img):
    output = img

    image = Image.open(img)
    width, height = image.size

    width_factor = 800 / width
    height_factor = 600 / height

    resizing_factor = min(width_factor, height_factor)

    new_width = int(width * resizing_factor)
    new_height = int(height * resizing_factor)

    # Resize the image
    resized_image = image.resize((new_width, new_height), Image.ANTIALIAS)

    new_image = Image.new("RGB", (800, 600), (255, 255, 255))
    new_image.paste(resized_image, ((800 - new_width) // 2, (600 - new_height) // 2))

    new_image.save(output)


def front_end():
    input_data = {}

    # scraping inputs
    ad_link = input("Ad link: ")
    input_data['ad_link'] = ad_link

    input_data['spider_name'] = domain_detector(ad_link)

    img_index_input = input('Images index (1,2,3 or 1:8): ')
    input_data['img_index'] = image_output(img_index_input)

    # # pdf inputs

    seller_name = input("Seller name: ")
    input_data['seller_name'] = seller_name

    seller_phone = input("Seller Phone: ")
    if seller_phone:
        input_data['seller_phone'] = seller_phone

    purchaser_name = input("Purchaser Name: ")
    if purchaser_name:
        input_data['purchaser_name'] = purchaser_name

    purchaser_phone = input("Purchaser Phone: ")
    if purchaser_phone:
        input_data['purchaser_phone'] = purchaser_phone

    purchaser_email = input("Purchaser Email: ")
    if purchaser_email:
        input_data['purchaser_email'] = purchaser_email

    shipping_fees = input('Shipping Fees: ')
    if shipping_fees:
        input_data['shipping_fees'] = float(shipping_fees)

    customs = input('Customs (optional): ')
    if customs:
        input_data['customs'] = float(customs)

    logistics_fees = input('Clearance and shipping: ')
    if logistics_fees:
        input_data['logistics_fees'] = float(logistics_fees)

    company_fees = input("G&O fees % (default is 7%): ")
    if company_fees:
        input_data['company_fees'] = float(company_fees)

    quotation_num = input("Quotation No: ")
    if quotation_num:
        input_data['quotation_num'] = quotation_num

    _date = input('Date (default is current date): ')
    if _date:
        input_data['date'] = _date

    return input_data


def main():
    input_data = front_end()

    if input_data['spider_name'] == 'SuchenMobileDe':
        calling_spider(spider_name=SuchenMobileDe, url=[input_data['ad_link']], img_idx=input_data['img_index'])
    else:
        calling_spider(spider_name=AutoScout24De, url=[input_data['ad_link']], img_idx=input_data['img_index'])

    car_data = read_car_data()

    download_image(images=car_data['car_images'])

    PdfGenerator(api_data=car_data, input_data=input_data)


if __name__ == "__main__":
    main()
    print("+-" * 20 + "Document is Ready" + "+-" * 20)

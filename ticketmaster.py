import scrapy
from selenium.webdriver import Chrome, ChromeOptions
#from scrapy.utils.project import get_project_settings
from scraping_project.items import EventItem
import time
import io
from pytesseract import pytesseract
from PIL import Image
import requests
import csv

# RUN THIS TO CRAWL & SAVE: scrapy crawl ticketmaster -t csv -o ticketmaster2.csv --loglevel=INFO

#Define path to tessaract.exe
path_to_tesseract = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'

#Point tessaract_cmd to tessaract.exe
pytesseract.tesseract_cmd = path_to_tesseract

def ocr_core(img):
    # Handles core OCR processing of images
    text = pytesseract.image_to_string(img)
    return text

class TicketMasterSpider(scrapy.Spider):
    #identity
    name = "ticketmaster"
    allowed_domains = ['www.ticketmaster.sg']

    def start_requests(self):
        driver_path = '/Users/mcsj_/Downloads/chromedriver_win32/chromedriver'
        driver = Chrome(executable_path = driver_path)
        options = ChromeOptions()
        options.headless = True
        driver = Chrome(executable_path=driver_path, options=options)
        driver.get('https://ticketmaster.sg/activity')
        time.sleep(2)
        i = 5
        while i<10:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            i=i+1
            time.sleep(2)

        xpath = '//div[@class="thumbnails"]/a'
        link_elements = driver.find_elements("xpath", xpath)
        for link_el in link_elements:
            href = link_el.get_attribute("href")
            yield scrapy.Request(url=href, callback=self.parse)

        driver.quit()


    def parse(self, response):
        # create dictionary
        item = EventItem()
        item['source'] = "ticketmaster"
        item['event_link'] = response.request.url
        item['name'] = response.css('#synopsisEventTitle::text').extract()
        item['event_date'] = response.css('#synopsisEventDate::text').extract()
        initial_price = response.xpath(''.join('//div[@id="prices-content"]//text()')).extract()
        item['price'] = "".join([t.strip("\t\n") for t in initial_price if t.strip("\t\n")])
        item['venue'] = response.css('#synopsisEventVenue::text').extract()
        src_url = response.css('#promoterContent img::attr(src)').extract()
        src = src_url[0]
        response = requests.get(src)
        img = Image.open(io.BytesIO(response.content))
        text = ocr_core(img)
        item['promoter'] = text

        yield item

        

        # # create time str to save with filename
        # timestr = time.strftime("%Y%m%d-%H%M%S")
        # # open the file in the write mode
        # new_file = 'ticketmaster_'
        # _file = new_file + timestr + '.csv'
        # try:
        #     with open(_file, 'w') as csvfile:
        #         for key in item.keys():
        #             csvfile.write("%s,%s\n"%(key,item[key]))
        # except IOError:
        #     print("I/O error")
    
# ADD URL TO ITEM
    



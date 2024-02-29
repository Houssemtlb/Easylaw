import scrapy
from scrapy import signals
import requests
from tqdm import tqdm
import os


class JoradpSpider(scrapy.Spider):
    data = {}
    name = 'joradp'
    start_urls = ['https://www.joradp.dz/HAR/Index.htm']

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(JoradpSpider, cls).from_crawler(
            crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed,
                                signal=signals.spider_closed)
        return spider

    def parse(self, response):
        # Step 2: Extract href attribute from the specified element
        href = "https://www.joradp.dz/JRN/ZA2024.htm"
        if href:

            # Step 3: Extract year from the href attribute
            currentYear = int(href.split('ZA')[1].split('.')[0])
            # Step 4: Make requests for each year from 2024 to 1964
            for year in range(currentYear, 1963, -1):
                url = f'https://www.joradp.dz/JRN/ZA{year}.htm'
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Referer': 'https://www.joradp.dz/HAR/ATitre.htm',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'frame',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-User': '?1',
                    'TE': 'trailers',
                }
                yield scrapy.Request(url, headers=headers, callback=self.parse_year, meta={'year': year})

    def parse_year(self, response):
        options = response.css(
            'form[name="zFrm2"] select[name="znjo"] option[value]:not(:empty)')
        year = response.meta['year']
        year_data = {year: [option.attrib['value'] for option in options]}
        self.data.update(year_data)

    def spider_closed(self, spider):
        base_url = "https://www.joradp.dz/FTP/JO-ARABE/"
        self.data = dict(sorted(self.data.items()))
        with open('pdf_numbers.txt', 'w') as f:
            f.write(f'{self.data}\n')

        for year, numbers in self.data.items():
            max = numbers[0]
            for number in tqdm(numbers, desc=f"Downloading PDFs for {year}"):
                if int(max) > 99:
                    pdf_url = f"{base_url}{year}/A{year}{number}.pdf"
                else:
                    pdf_url = f"{base_url}{year}/A{year}0{number}.pdf"

                response = requests.get(pdf_url, stream=True)

                if response.status_code == 200:
                    local_directory = f"joradp_pdfs/{year}"
                    local_file_path = f"{local_directory}/{year}_{number}.pdf"

                    # Create directory if it doesn't exist
                    os.makedirs(local_directory, exist_ok=True)

                    with open(local_file_path, 'wb') as pdf_file:
                        for chunk in response.iter_content(chunk_size=128):
                            pdf_file.write(chunk)

                    print(f"Downloaded: {year}_{number}.pdf")
                else:
                    print(
                        f"Failed to download {year}_{number}.pdf. Status Code: {response.status_code}")

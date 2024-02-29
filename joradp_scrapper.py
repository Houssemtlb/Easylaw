import scrapy

class JoradpSpider(scrapy.Spider):
    name = 'joradp'
    start_urls = ['https://www.joradp.dz/HAR/Index.htm']

    def parse(self, response):
        # Step 2: Extract href attribute from the specified element
        href = response.css('a[title="عرض الجرائد"]::attr(href)').get()
        
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
        # Step 5: Extract options for the current year
        options = response.css('form[name="zFrm2"] select[name="znjo"] option')
        year = response.meta['year']
        year_data = {year: [option.attrib['value'] for option in options]}

        # Write data to a file
        with open('output.txt', 'a') as f:
            f.write(f'{year_data}\n')

        # Step 6: Print the data structure
        self.log(year_data)

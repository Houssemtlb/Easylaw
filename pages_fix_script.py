import scrapy
from scrapy import signals
from datetime import date as dt
from sqlalchemy import and_, create_engine, Column, Integer, String, Date,Boolean,Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from bs4 import BeautifulSoup

Base = declarative_base()


class LawText(Base):
    __tablename__ = "laws"
    id = Column(Integer, primary_key=True, autoincrement=False)
    text_type = Column(String)
    text_number = Column(String)
    journal_date = Column(Date)
    journal_num = Column(Integer)
    journal_page = Column(Integer)
    signature_date = Column(Date)
    ministry = Column(String)
    content = Column(String)
    field = Column(String, default="")
    long_content = Column(Text,default="")
    page_fixed = Column(Boolean, default=False)


engine = create_engine("postgresql://postgres:postgres@localhost:5432/easylaw")

Session = sessionmaker(bind=engine)
session = Session()


class JoradpSpider(scrapy.Spider):
    data = {}
    name = 'joradp'
    currentYear = 0
    start_urls = ['https://www.joradp.dz/HAR/Index.htm']

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(JoradpSpider, cls).from_crawler(
            crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed,
                                signal=signals.spider_closed)
        return spider

    def parse(self, response):
        Base.metadata.create_all(engine)
        # Step 2: Extract href attribute from the specified element
        href = "https://www.joradp.dz/JRN/ZA2024.htm"
        if href:

            # Step 3: Extract year from the href attribute
            self.currentYear = int(href.split('ZA')[1].split('.')[0])
            # Step 4: Make requests for each year from 2024 to 1964
            for year in range(self.currentYear, 1963, -1):
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

        if len(self.data) == (self.currentYear - 1963):
            yield scrapy.Request(url="https://www.joradp.dz", callback=self.process_laws)

    def process_laws(self, response):
        self.data = dict(sorted(self.data.items()))

        for year, numbers in self.data.items():
            if year < 2000:
                for number in numbers:
                    # fixing the laws for every newspaper
                    if 1961 < year <= 1983:
                        Lien = "Jo6283"
                    elif 1983 < year:
                        Lien = "Jo8499"

                    if int(number) < 10:
                        processed_number = f"00{int(number)}"
                    elif 10 <= int(number) < 100:
                        processed_number = f"0{int(number)}"
                    else:
                        processed_number = f"{int(number)}"

                    base_url = f"https://www.joradp.dz/{Lien}/{year}/{processed_number}/A_Pag1.htm"

                    yield scrapy.Request(base_url, callback=self.parse_law_text, meta={'year': year, 'number': processed_number})

    def parse_law_text(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')
        table_rows = soup.find_all('tr')
        incorrect_numbers = [row.text.strip() for row in table_rows]

        incorrect_numbers = incorrect_numbers[1:]
        if (incorrect_numbers[0] != '1'):
            # here we performe our correction in the db
            correctPage = 1

            start_date = dt(int(response.meta['year']), 1, 1)
            end_date = dt(int(response.meta['year']), 12, 31)

            for incorrect_number in incorrect_numbers:
                rowsToCorrect = session.query(LawText).filter(
                    and_(
                        LawText.journal_date >= start_date,
                        LawText.journal_date <= end_date,
                        LawText.journal_page == incorrect_number,
                        LawText.journal_num == int(response.meta['number'])
                    )
                ).all()

                if (rowsToCorrect):
                    for row in rowsToCorrect:
                        row.journal_page = correctPage
                    session.commit()
                correctPage += 1

    def spider_closed(self, spider):
        # Perform cleanup or final operations when the spider is closed
        pass

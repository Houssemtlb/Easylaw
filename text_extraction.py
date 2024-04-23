import logging
from sqlalchemy.orm import declarative_base
from sqlalchemy import and_, create_engine, Column, Integer, String, Date, Boolean, Text
from sqlalchemy.orm import sessionmaker
import os
from datetime import date as dt
from fuzzywuzzy import fuzz


def setup_logger(name, log_file, level=logging.INFO):
    """Function to setup as many loggers as you want"""

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s : \n %(message)s \n"
    )
    handler = logging.FileHandler(
        log_file, encoding="utf-8", mode="w"
    )  # use 'a' if you want to keep history or 'w' if you want to override file content
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    # Prevent the logger from propagating messages to the root logger
    logger.propagate = False

    return logger


main_logger = setup_logger(
    f".\pdf_text_extraction_logs",
    f".\pdf_text_extraction_logs.log",
)


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
    long_content = Column(Text, default="")
    page_fixed = Column(Boolean, default=False)


class Newspaper(Base):
    __tablename__ = "official_newspaper"
    id = Column(String, primary_key=True)
    year = Column(String)
    number = Column(String)


engine = create_engine('postgresql://postgres:postgres@localhost:5432/easylaw')
Session = sessionmaker(bind=engine)
session = Session()

keywords = ['أمر', 'منشور', 'منشور وزاري مشترك',
            'لائحة', 'مداولة', 'مداولة م-أ-للدولة',
            'مرسوم', 'مرسوم تنفيذي', 'مرسوم تشريعي',
            'مرسوم رئاسي', 'مقرر', 'مقرر وزاري مشترك',
            'إعلان', 'نظام', 'اتفاقية', 'تصريح', 'تقرير',
            'تعليمة', 'تعليمة وزارية مشتركة', 'جدول', 'رأي',
            'قانون', 'قانون عضوي', 'قرار', 'قرار ولائي', 'قرار وزاري مشترك',
            'أوامر', 'مناشير', 'مناشير وزارية مشتركة',
            'لوائح', 'مداولات', 'مداولات م-أ-للدولة',
            'مراسيم', 'مراسيم تنفيذية', 'مراسيم تشريعية',
            'مراسيم رئاسية', 'مقررات', 'مقررات وزارية مشتركة',
            'إعلانات', 'نظم', 'اتفاقيات',
            'تصاريح', 'تقارير', 'تعليمات', 'تعليمات وزارية مشتركة',
            'جداول', 'آراء', 'قوانين', 'قوانين عضوية',
            'قرارات', 'قرارات ولائية', 'قرارات وزارية مشتركة']


def iterate_law_texts():
    try:
        for news_paper in session.query(Newspaper).all():

            # Construct the text of the rest of the journal starting from the related page
            directory = f'joradp_pdfs\{news_paper.year}\{news_paper.year}_{news_paper.number}'
            txt_files = [file for file in os.listdir(directory) if (
                file.endswith('.txt') and int(file.split('.')[0]) >= 1)]
            txt_files = sorted(txt_files, key=lambda x: int(x.split('.')[0]))

            # concatenate all th text of txt_files in the directory
            lawsStartingPage = []
            for law in session.query(LawText).filter(
                and_(
                    LawText.journal_date >= dt(news_paper.year, 1, 1),
                    LawText.journal_date <= dt(news_paper.year, 12, 31),
                    LawText.journal_num == news_paper.number,
                )
            ).all():

                lawsStartingPage.append(
                    {'id': law.id, 'pages': law.journal_page})
                lawsStartingPage = sorted(
                    lawsStartingPage, key=lambda x: x['pages'])
            lawsPagesRanges = transform_to_page_ranges(lawsStartingPage)

            
            
            for object in lawsPagesRanges:
                law = session.query(LawText).filter(
                    LawText.id == object['id']).first()
                text_number = law.text_number
                if text_number != "":
                    law_title = f"{law.text_type} رقم {law.text_number}"
                else:
                    law_title = f"{law.text_type}"

                long_text = ''
                for page in object['pages']:
                    # if last element in the list
                    if page != object['pages'][-1]:
                        with open(f'{directory}/{page}.txt', 'r', encoding='utf-8') as f:
                            long_text += f.read()
                    else:
                        for file in txt_files:
                            file_page = int(file.split('.')[0])
                            if int(file_page) >= int(page):
                                with open(f'{directory}/{file}', 'r', encoding='utf-8') as f:
                                    long_text += f.read()
                    
                trimed_long_text = trim_before_desired_name(
                    long_text, law_title, text_number)

                main_logger.info(f"title : {law_title}")
                main_logger.info(f"text : {trimed_long_text}")

                #insert the long text in the database
                law.long_content = trimed_long_text
                session.commit()

    except Exception as e:
        print(f"An error occurred: {e}")


def transform_to_page_ranges(data):
    page_ranges = []
    for i in range(len(data)):
        law_title = data[i]['id']
        starting_page = data[i]['pages']
        if i < len(data) - 1:
            next_starting_page = data[i + 1]['pages']
            page_range = list(range(starting_page, next_starting_page))
        else:
            page_range = list(range(starting_page, starting_page + 1))
        if not page_range:
            page_range = [starting_page]

        page_ranges.append({'id': law_title, 'pages': page_range})
    return page_ranges


def trim_before_desired_name(long_text, desired_name, text_number):
    lines = long_text.split('\n')
    desired_line_index = None

    # Find the line index where the desired name string is present
    for i, line in enumerate(lines):
        words = line.split()
        num_words_to_compare = len(desired_name.split())
        if len(words) >= num_words_to_compare:
            initial_words = ' '.join(words[:num_words_to_compare])

            if fuzz.ratio(desired_name, initial_words) >= 60:
                # if there is an exact match with text number
                if text_number != None:
                    numbers = text_number.split('-')
                    try:
                        if numbers[1] in line:
                            desired_line_index = i
                            break
                    except:
                        desired_line_index = i
                        break
                else:
                    desired_line_index = i
                    break

    # Remove lines before the desired line
    if desired_line_index is not None:
        lines = lines[desired_line_index:]
        return '\n'.join(lines)
    else:
        return long_text


def find_lines_with_laws(long_text, year, number):
    lines = long_text.split('\n')
    found_line_indexes = []
    prepared_law_texts = []

    law_texts = session.query(LawText).filter(
        and_(
            LawText.journal_date >= dt(int(year), 1, 1),
            LawText.journal_date <= dt(int(year), 12, 31),
            LawText.journal_num == int(number)
        )
    ).all()

    for law_text in law_texts:
        text_number = law_text.text_number
        if text_number != None:
            law_title = f"{law_text.text_type} رقم {law_text.text_number}"
        else:
            law_title = f"{law_text.text_type}"
        prepared_law_texts.append(
            {'law_title': law_title, 'text_number': law_text.text_number})

    main_logger.info(f"prepared_law_texts : {prepared_law_texts}")

    for i, line in enumerate(lines):
        words = line.split()

        for law in prepared_law_texts:
            num_words_to_compare = len(law["law_title"].split())
            if len(words) >= num_words_to_compare:
                initial_words = ' '.join(words[:num_words_to_compare])

                if fuzz.partial_ratio(law["law_title"], initial_words) >= 90:
                    if law["text_number"] != None:
                        numbers = law["text_number"]
                        try:
                            if numbers[1] in line:
                                found_line_indexes.append(
                                    {'index': i, 'law_title': law["law_title"]})
                                break
                        except:
                            found_line_indexes.append(
                                {'index': i, 'law_title': law["law_title"]})
                            break

    return found_line_indexes




if __name__ == "__main__":
    iterate_law_texts()


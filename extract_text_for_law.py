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


before_logger = setup_logger(
    f".\pdf_text_extraction_logs_before",
    f".\pdf_text_extraction_logs_before.log",
)
after_logger = setup_logger(
    f".\pdf_text_extraction_logs_after",
    f".\pdf_text_extraction_logs_after.log",
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
    year = Column(String),
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
        for news_paper in session.query(Newspaper).filter(
                    and_(
                        LawText.journal_date >= dt(2009, 1, 1),
                        LawText.journal_date <= dt(2009, 12, 31),
                    )
                ).all():

            pass    
        

    except Exception as e:
        print(f"An error occurred: {e}")


def trim_before_desired_name(long_text, desired_name, text_number):
    lines = long_text.split('\n')
    desired_line_index = None

    # Find the line index where the desired name string is present
    for i, line in enumerate(lines):
        words = line.split()
        num_words_to_compare = len(desired_name.split())
        if len(words) >= num_words_to_compare:
            initial_words = ' '.join(words[:num_words_to_compare])

            if fuzz.partial_ratio(desired_name, initial_words) >= 60:
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

    # Remove lines before the desired line
    if desired_line_index is not None:
        lines = lines[desired_line_index:]
        return '\n'.join(lines)
    else:
        return long_text


def trim_after_desired_name(long_text, firstPage):
    lines = long_text.split('\n')
    desired_line_index = None
    count = 0
    stop = False

    # Find the line index where the desired name string is present
    for i, line in enumerate(lines):
        words = line.split()
        for keyword in keywords:
            num_words_to_compare = len(keyword.split())
            if len(words) >= num_words_to_compare:
                initial_words = ' '.join(words[:num_words_to_compare])

                if fuzz.partial_ratio(keyword, initial_words) >= 90:
                    count += 1
                    if (firstPage) and count == 2:
                        desired_line_index = i
                        stop = True
                        break
                    elif (not firstPage):
                        desired_line_index = i
                        stop = True
                    break

    # Remove lines before the desired line
    if desired_line_index is not None:
        lines = lines[:desired_line_index]
        return ('\n'.join(lines), stop)
    else:
        return (long_text, stop)


if __name__ == "__main__":
    iterate_law_texts()

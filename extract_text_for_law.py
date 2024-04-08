from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Date, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker
import os


Base = declarative_base()


class LawText(Base):
    __tablename__ = "text"
    id = Column(Integer, primary_key=True, autoincrement=False)
    text_type = Column(String)
    text_number = Column(String)
    journal_date = Column(Date)
    journal_num = Column(Integer)
    journal_page = Column(Integer)
    signature_date = Column(Date)
    ministry = Column(String)
    content = Column(String)


engine = create_engine('postgresql://postgres:postgres@localhost:5432/easylaw')
Session = sessionmaker(bind=engine)
session = Session()


def iterate_law_texts():
    try:
        # Query all rows from the LawText table
        law_texts = session.query(LawText).all()

        # Iterate through each LawText object
        for law_text in law_texts:
            # Retrieve the desired fields
            journal_page = law_text.journal_page
            journal_num = law_text.journal_num
            journal_date = law_text.journal_date
            
            # Extract the year from journal_date
            journal_year = journal_date.year
            
            # Construct the file path to the .txt file
            txt_file_path = os.path.join('joradp_pdfs', str(journal_year), f'{journal_year}_{journal_num}', f'{journal_num}.txt')
            
            # Read the content of the .txt file
            with open(txt_file_path, 'r', encoding='utf-8') as file:
                page_text = file.read()
            
            # Print the retrieved data
            print(f"Journal Page: {journal_page}, Journal Num: {journal_num}, Journal Date: {journal_date}")
            print(f"Page Text: {page_text}")
            
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    iterate_law_texts()


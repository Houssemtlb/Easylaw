import multiprocessing
import os
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options
from datetime import date as dt
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import ARRAY

import logging


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


class Association(Base):
    __tablename__ = "associations"
    id = Column(Integer, primary_key=True)
    assoc_nom = Column(String)
    id_out = Column(Integer)
    ids_in = Column(ARRAY(Integer))


engine = create_engine("postgresql://postgres:postgres@localhost:5432/easylaw")

arabic_months = {
    "يناير": "01",
    "فبراير": "02",
    "مارس": "03",
    "أبريل": "04",
    "مايو": "05",
    "يونيو": "06",
    "يوليو": "07",
    "غشت": "08",
    "سبتمبر": "09",
    "أكتوبر": "10",
    "نوفمبر": "11",
    "ديسمبر": "12",
}

total_number_of_laws = 0
total_number_of_associations = 0


def scrape_law_data(law_type):
    global total_number_of_laws
    global total_number_of_associations

    number_of_pages = 0
    i = 0
    j = 0
    lawTexts = []
    allAssoc = []
    number_of_laws_in_this_type = 0
    while i <= number_of_pages:
        i = 0
        print(f"TRY NUMBER {j + 1} FOR {law_type}!!!")

        try:
            options = Options()
            #options.add_argument("--headless=new")
            driver = webdriver.Firefox(options=options)

            # Open the website
            driver.get("https://www.joradp.dz/HAR/Index.htm")

            # Switch to the frame with src="ATitre.htm"
            driver.switch_to.frame(
                driver.find_element(By.XPATH, '//frame[@src="ATitre.htm"]')
            )

            # Wait for an element on the page to indicate that it's fully loaded
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "/html/body/div/table[2]/tbody/tr/td[3]/a")
                )
            )

            # Now you can interact with elements inside this frame
            search_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "/html/body/div/table[2]/tbody/tr/td[3]/a")
                )
            )
            search_link.click()

            # Switch back to the default content before switching to another frame
            driver.switch_to.default_content()
            # Switch to the frame with name="FnCli"
            driver.switch_to.frame(
                driver.find_element(By.XPATH, '//frame[@name="FnCli"]')
            )

            # select category
            select_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "znat"))
            )

            select_object = Select(select_input)
            select_object.select_by_visible_text(law_type)

            # Find the input field and enter '01/01/1964'
            date_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "znjd"))
            )
            date_input.clear()
            date_input.send_keys("01/01/1964")

            # Click on the "بــحـــث" button
            search_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//a[contains(@title, "تشغيل البحث")]')
                )
            )
            search_button.click()

            display_settings_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "/html/body/div/table[1]/tbody/tr/td[1]/a")
                )
            )
            display_settings_link.click()

            pages_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "daff"))
            )
            pages_input.clear()
            pages_input.send_keys("200")

            irsal_link = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "/html/body/div/form/table[2]/tbody/tr[1]/td/a")
                )
            )
            irsal_link.click()

            numberOfPages = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="tex"]'))
            )
            number_of_pages_text = numberOfPages.text
            pattern = r"العدد (\d+)"
            match = re.search(pattern, number_of_pages_text)

            number_of_laws = 0
            if match:
                number_of_laws = match.group(1)

            number_of_pages = int(int(number_of_laws) / 200)

            directory = f"./pages_scraping_logs/{law_type}"
            os.makedirs(directory, exist_ok=True)

            while i <= number_of_pages:
                lawTexts.clear()
                allAssoc.clear()
                matching_rows = driver.find_elements(
                    By.XPATH, '//tr[@bgcolor="#78a7b9"]'
                )
                # Iterate through the matching rows
                page_logger = setup_logger(
                    f"page_{i}_{law_type}",
                    f"./pages_scraping_logs/{law_type}/page_{i}.log",
                )
                page_logger.info(f"Starting scrape for {law_type}, page {i}")
                row_number = 0
                for row in matching_rows:
                    row_number += 1
                    log_line = f"----------------- \n row: {row_number}\n"
                    page_logger.info(log_line)
                    object = {
                        "id": -1,
                        "textType": "",
                        "textNumber": "",
                        "journalDate": "",
                        "journalNum": "",
                        "journalPage": "",
                        "signatureDate": "",
                        "ministry": "",
                        "content": "",
                    }
                    # Find the a element within the current row
                    link_element = row.find_element(By.XPATH, ".//td[2]/a")
                    # Get the href attribute value and append it to the array
                    href_value = link_element.get_attribute("href")
                    page = re.search(
                        r'JoOpen\("(\d+)", *"(\d+)", *"(\d+)", *"([A-Za-z]+)"\)',
                        href_value,
                    )
                    if page:
                        (
                            journalYear,
                            object["journalNum"],
                            object["journalPage"],
                            letter,
                        ) = page.groups()

                    id_element = row.find_element(By.XPATH, ".//td[1]/a")
                    id_element_href = id_element.get_attribute("href")
                    match = re.search(r"#(\d+)", id_element_href)
                    id_number = match.group(1)
                    object["id"] = int(id_number)

                    next_siblings = []
                    current_element = row
                    assocObject = {"assoc": "", "idOut": object["id"], "idsIn": []}
                    sibling_number = 0
                    while True:
                        sibling_number += 1
                        log_line = f"----------------- \n Following sibling number: {sibling_number}\n"
                        page_logger.info(log_line)
                        following_sibling_found = current_element.find_elements(
                            By.XPATH, "following-sibling::tr[1]"
                        )
                        try:
                            if following_sibling_found:
                                following_sibling = following_sibling_found[0]
                                log_line = (
                                    f" ----------------- \n Following sibling found\n"
                                )
                                page_logger.info(log_line)

                                log_line = f"Following sibling Text: \n {following_sibling.text}\n"
                                page_logger.info(log_line)

                                sibling_bgcolor = following_sibling.get_attribute(
                                    "bgcolor"
                                )
                                log_line = f"Sibling bgcolor: {sibling_bgcolor}\n"
                                page_logger.info(log_line)

                                if sibling_bgcolor == "#78a7b9":
                                    log_line = f"***********\n Next law found\n ***********\n**************\n"
                                    page_logger.info(log_line)

                                    if assocObject["assoc"] != "":
                                        log_line = f"assocObject: {assocObject}\n"
                                        page_logger.info(log_line)

                                        allAssoc.append(assocObject.copy())
                                        log_line = f"All law Assoc: {allAssoc}\n"
                                        page_logger.info(log_line)

                                    break
                                else:
                                    td_elements = following_sibling.find_elements(
                                        By.XPATH, ".//td"
                                    )
                                    law_td = td_elements[0]
                                    marg = law_td.get_attribute("colspan")
                                    log_line = f"Colspan for law_td: {marg}\n"
                                    page_logger.info(log_line)

                                    if marg == "6":
                                        next_siblings.append(following_sibling)
                                        log_line = f"Added to next_siblings\n"
                                        page_logger.info(log_line)
                                    else:
                                        assoc_td = td_elements[1]
                                        marg = assoc_td.get_attribute("colspan")
                                        log_line = f"Colspan for assoc_td: {marg}\n"
                                        page_logger.info(log_line)

                                        if marg == "5":
                                            if assocObject["assoc"] != "":
                                                log_line = (
                                                    f"assocObject: {assocObject}\n"
                                                )
                                                page_logger.info(log_line)
                                                allAssoc.append(assocObject.copy())
                                                log_line = f"All law Assoc until now: {allAssoc}\n"
                                                page_logger.info(log_line)

                                            assoc = assoc_td.find_element(
                                                By.TAG_NAME, "font"
                                            )
                                            assocObject = {
                                                "assoc": "",
                                                "idOut": object["id"],
                                                "idsIn": [],
                                            }
                                            assocObject["assoc"] = assoc.text
                                            log_line = (
                                                f"Association text: {assoc.text}\n"
                                            )
                                            page_logger.info(log_line)

                                        else:
                                            law_td = td_elements[0]
                                            marg = law_td.get_attribute("colspan")
                                            log_line = f"Colspan for law_td (2nd check): {marg}\n"
                                            page_logger.info(log_line)

                                            if marg == "2":
                                                if len(td_elements) == 3:
                                                    law_td = td_elements[2]
                                                    color = law_td.get_attribute(
                                                        "bgcolor"
                                                    )
                                                    log_line = (
                                                        f"Law_td bgcolor: {color}\n"
                                                    )
                                                    page_logger.info(log_line)

                                                    if color == "#9ec7d7":
                                                        law_td = td_elements[1]
                                                        id_element = (
                                                            law_td.find_element(
                                                                By.TAG_NAME, "a"
                                                            )
                                                        )
                                                        id_element_href = (
                                                            id_element.get_attribute(
                                                                "href"
                                                            )
                                                        )
                                                        log_line = f"Law ID href: {id_element_href}\n"
                                                        page_logger.info(log_line)

                                                        match = re.search(
                                                            r"#(\d+)", id_element_href
                                                        )
                                                        id_number = -1
                                                        if match:
                                                            id_number = match.group(1)
                                                            assocObject["idsIn"].append(
                                                                id_number
                                                            )
                                                            log_line = (
                                                                f"Law ID: {id_number}\n"
                                                            )
                                                            page_logger.info(log_line)
                                                        else:
                                                            pass
                                                            log_line = f"Error finding law id!\n"
                                                            page_logger.info(log_line)

                                                    else:
                                                        pass
                                                        log_line = f"Processing another law for the association\n"
                                                        page_logger.info(log_line)
                                                else:
                                                    pass
                                                    # association law data
                                                    log_line = f"association law data\n"
                                                    page_logger.info(log_line)
                                            else:
                                                pass
                                                log_line = f"No matching conditions for association law\n"
                                                page_logger.info(log_line)
                            else:
                                pass
                                # the last element in the page
                                break
                        except Exception as e:
                            log_line = f"Error in processing: {e}\n"
                            page_logger.info(log_line)

                        current_element = following_sibling

                    if len(next_siblings) == 4:
                        var1 = next_siblings[0].text
                        object["textType"] = law_type
                        pattern = r"رقم (\S+)"
                        match = re.search(pattern, var1)
                        if match:
                            textNumber = match.group(1)
                        else:
                            textNumber = ""
                        object["textNumber"] = textNumber

                        # Define the regular expression pattern
                        pattern = r"في (\d+ [^\s]+ \d+)"
                        # Use re.search to find the match
                        match = re.search(pattern, var1)
                        # Check if there is a match and extract the result
                        if match:
                            full_date_str = match.group(1)
                            signatureDay, signatureMonth, signatureYear = (
                                full_date_str.split()
                            )
                            signatureMonth = arabic_months[signatureMonth]

                            object["signatureDate"] = (
                                signatureYear
                                + "-"
                                + str(signatureMonth)
                                + "-"
                                + signatureDay
                            )

                            object["signatureDate"] = dt.fromisoformat(
                                object["signatureDate"]
                            )

                        object["ministry"] = next_siblings[1].text

                        date = next_siblings[2].text
                        # Define the regular expression pattern
                        pattern = r"في (.*?)،"
                        # Use re.search to find the match
                        match = re.search(pattern, date)
                        # Check if there is a match and extract the result
                        if match:
                            jornal_date_str = match.group(1)
                            journalDay, journalMonth, _ = jornal_date_str.split()
                            journalMonth = arabic_months[journalMonth]
                            object["journalDate"] = (
                                journalYear + "-" + str(journalMonth) + "-" + journalDay
                            )

                            object["journalDate"] = dt.fromisoformat(
                                object["journalDate"]
                            )

                        object["content"] = next_siblings[3].text
                        lawTexts.append(object.copy())

                    elif len(next_siblings) == 3:
                        var1 = next_siblings[0].text
                        object["textType"] = law_type
                        pattern = r"رقم (\S+)"
                        match = re.search(pattern, var1)
                        if match:
                            textNumber = match.group(1)
                        else:
                            textNumber = ""
                        object["textNumber"] = textNumber

                        # Define the regular expression pattern
                        pattern = r"في (\d+ [^\s]+ \d+)"
                        # Use re.search to find the match
                        match = re.search(pattern, var1)
                        # Check if there is a match and extract the result
                        if match:
                            full_date_str = match.group(1)
                            signatureDay, signatureMonth, signatureYear = (
                                full_date_str.split()
                            )
                            signatureMonth = arabic_months[signatureMonth]

                            object["signatureDate"] = (
                                signatureYear
                                + "-"
                                + str(signatureMonth)
                                + "-"
                                + signatureDay
                            )

                            object["signatureDate"] = dt.fromisoformat(
                                object["signatureDate"]
                            )

                        date = next_siblings[1].text
                        # Define the regular expression pattern
                        pattern = r"في (.*?)،"
                        # Use re.search to find the match
                        match = re.search(pattern, date)
                        # Check if there is a match and extract the result
                        if match:
                            jornal_date_str = match.group(1)
                            journalDay, journalMonth, _ = jornal_date_str.split()
                            journalMonth = arabic_months[journalMonth]
                            object["journalDate"] = (
                                journalYear + "-" + str(journalMonth) + "-" + journalDay
                            )

                            object["journalDate"] = dt.fromisoformat(
                                object["journalDate"]
                            )

                        object["content"] = next_siblings[2].text
                        lawTexts.append(object.copy())
                    else:
                        log_line = f" \n \n \n ERROR\n"
                        page_logger.info(log_line)

                total_number_of_laws += len(lawTexts)
                number_of_laws_in_this_type += len(lawTexts)
                storeLawText(lawTexts)

                log_line = f" \n \n \n ~~~~~~~~~~~~~~~~ \n lawTexts {lawTexts}\n"
                page_logger.info(log_line)
                log_line = f" \n \n \n ~~~~~~~~~~~~~~~~ \n length of lawTexts {len(lawTexts)}\n"
                page_logger.info(log_line)

                print("total_number_of_laws until now: ", total_number_of_laws)

                total_number_of_associations += len(allAssoc)
                storeLawAssociations(allAssoc)

                log_line = f" \n \n \n ~~~~~~~~~~~~~~~~ \n allAssoc {allAssoc}\n"
                page_logger.info(log_line)
                log_line = f" \n \n \n ~~~~~~~~~~~~~~~~ \n length of allAssoc {len(allAssoc)}\n"
                page_logger.info(log_line)

                log_line = f" \n Finished scraping page {i} of {law_type} with {len(lawTexts)} law and {len(allAssoc)} assoc \n"
                page_logger.info(log_line)
                print(log_line)

                if (i != number_of_pages):
                    next_page_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//a[@href=\"javascript:Sauter('a',3);\"]")
                        )
                    )
                    next_page_button.click()
                    
                    expected_number = ((i+1) * 200) + 1

                    def check_page(driver):
                        element_text = driver.find_element(By.XPATH,'//*[@id="tex"]').text
                        pattern = r"من (\d+) إلى"
                        match = re.search(pattern, element_text)
                        if match:
                            found_number = int(match.group(1))
                            print(f"Found text: '{element_text}'. Extracted number: {found_number}. Expected number: {expected_number}.")
                            return found_number == expected_number
                        else:
                            print(f"No match found in text: '{element_text}'")
                            return False

                    print("expected_number", expected_number)
                    WebDriverWait(driver, 180, 2).until(check_page)
                    print(f"Successfully navigated to page {i + 1}")

                i = i + 1

        except TimeoutException as e:
            total_number_of_laws -= number_of_laws_in_this_type
            log_line = f"TimeoutException: {e} RETRYING..."
            print(log_line)
        finally:
            driver.quit()
            j += 1

    log_line = f"PROGRAM ENDED AFTER {j + 1} TRIES FOR {law_type}!!!"
    print(log_line)


def storeLawText(lawTexts):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        for law_text in lawTexts:
            # Check if the law text already exists
            existing_law_text = session.query(LawText).get(law_text["id"])
            if existing_law_text:
                # Update existing record
                existing_law_text.text_type = law_text["textType"]
                existing_law_text.text_number = law_text["textNumber"]
                existing_law_text.journal_date = law_text["journalDate"]
                existing_law_text.journal_num = law_text["journalNum"]
                existing_law_text.journal_page = law_text["journalPage"]
                existing_law_text.signature_date = law_text["signatureDate"]
                existing_law_text.ministry = law_text["ministry"]
                existing_law_text.content = law_text["content"]
            else:
                # Insert new record
                new_law_text = LawText(
                    id=law_text["id"],
                    text_type=law_text["textType"],
                    text_number=law_text["textNumber"],
                    journal_date=law_text["journalDate"],
                    journal_num=law_text["journalNum"],
                    journal_page=law_text["journalPage"],
                    signature_date=law_text["signatureDate"],
                    ministry=law_text["ministry"],
                    content=law_text["content"],
                )
                session.add(new_law_text)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error inserting/updating law text: {e}")
    finally:
        session.close()


def storeLawAssociations(associations):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        for assoc_data in associations:
            # Create a new Association object
            assoc_object = Association(
                id_out=assoc_data["idOut"],
                assoc_nom=assoc_data["assoc"],
                ids_in=assoc_data["idsIn"],
            )
            session.add(assoc_object)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error storing associations: {e}")
    finally:
        session.close()


if __name__ == "__main__":

    # Create database tables
    Base.metadata.create_all(engine)

    # Initialize ChromeOptions
    options = Options()
    #options.add_argument("--headless=new")
    driver = webdriver.Firefox(options=options)

    # Open the website
    driver.get("https://www.joradp.dz/HAR/Index.htm")

    # Switch to the frame with src="ATitre.htm"
    driver.switch_to.frame(driver.find_element(By.XPATH, '//frame[@src="ATitre.htm"]'))

    # Wait for an element on the page to indicate that it's fully loaded
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "/html/body/div/table[2]/tbody/tr/td[3]/a")
        )
    )

    # Now you can interact with elements inside this frame
    search_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "/html/body/div/table[2]/tbody/tr/td[3]/a")
        )
    )
    search_link.click()

    # Switch back to the default content before switching to another frame
    driver.switch_to.default_content()
    # Switch to the frame with name="FnCli"
    driver.switch_to.frame(driver.find_element(By.XPATH, '//frame[@name="FnCli"]'))

    # Find the input field and enter '01/01/1964'
    select_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "znat"))
    )
    select_object = Select(select_input)

    law_types = []
    options = select_object.options
    for option in options:
        law_types.append(option.text)
    law_types = law_types[1:]
    print(law_types)
    driver.quit()

    law_types_iterator = iter(law_types)
    with multiprocessing.Pool(processes=3) as pool:
        for result in pool.imap(scrape_law_data, law_types_iterator):
            pass

    print("total_number_of_laws: ", total_number_of_laws)
    print("total_number_of_associations: ", total_number_of_associations)

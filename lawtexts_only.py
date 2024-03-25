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
from selenium.webdriver.chrome.options import Options
from datetime import date as dt
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class LawText(Base):
    __tablename__ = 'text'
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

arabic_months = {
    'يناير': '01',
    'فبراير': '02',
    'مارس': '03',
    'أبريل': '04',
    'مايو': '05',
    'يونيو': '06',
    'يوليو': '07',
    'غشت': '08',
    'سبتمبر': '09',
    'أكتوبر': '10',
    'نوفمبر': '11',
    'ديسمبر': '12'
}


def scrape_law_data(law_type):
    with open(f'.\\scraping_logs\\{law_type}.txt', 'w', encoding='utf-8') as file:

        j = 0

        while (True):
            timeoutCounter = 0
            finish = False
            i = 0
            lawTexts = []
            file.write(f"TRY NUMBER {j + 1} FOR {law_type}!!! \n")
            try:
                options = Options()
                options.add_argument("--headless=new")
                driver = webdriver.Chrome(options=options)

                # Open the website
                driver.get('https://www.joradp.dz/HAR/Index.htm')

                # Switch to the frame with src="ATitre.htm"
                driver.switch_to.frame(driver.find_element(
                    By.XPATH, '//frame[@src="ATitre.htm"]'))

                # Wait for an element on the page to indicate that it's fully loaded
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '/html/body/div/table[2]/tbody/tr/td[3]/a'))
                )

                # Now you can interact with elements inside this frame
                search_link = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '/html/body/div/table[2]/tbody/tr/td[3]/a'))
                )
                search_link.click()

                # Switch back to the default content before switching to another frame
                driver.switch_to.default_content()
                # Switch to the frame with name="FnCli"
                driver.switch_to.frame(driver.find_element(
                    By.XPATH, '//frame[@name="FnCli"]'))

                # Find the input field and enter '01/01/1964'
                select_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, 'znat'))
                )

                select_object = Select(select_input)
                select_object.select_by_visible_text(law_type)

                # Find the input field and enter '01/01/1964'
                date_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, 'znjd'))
                )
                date_input.clear()
                date_input.send_keys('01/01/1964')

                # Click on the "بــحـــث" button
                search_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '//a[contains(@title, "تشغيل البحث")]'))
                )
                search_button.click()

                display_settings_link = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '/html/body/div/table[1]/tbody/tr/td[1]/a'))
                )
                display_settings_link.click()

                pages_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, 'daff'))
                )
                pages_input.clear()
                pages_input.send_keys('200')

                irsal_link = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '/html/body/div/form/table[2]/tbody/tr[1]/td/a'))
                )
                irsal_link.click()

                numberOfPages = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="tex"]'))
                )
                number_of_pages_text = numberOfPages.text
                pattern = r"العدد (\d+)"
                match = re.search(pattern, number_of_pages_text)

                number_of_laws = 0
                if match:
                    number_of_laws = match.group(1)

                number_of_pages = int(int(number_of_laws) / 200)

                while (True):
                    lawTexts = []
                    matching_rows = driver.find_elements(
                        By.XPATH, '//tr[@bgcolor="#78a7b9"]')
                    # Iterate through the matching rows
                    for row in matching_rows:
                        object = {'id': -1, 'textType': '', 'textNumber': '', 'journalDate': dt.fromisoformat('9999-12-31'), 'journalNum': '',
                                  'journalPage': '', 'signatureDate': dt.fromisoformat('9999-12-31'), 'ministry': '', 'content': ''}
                        # Find the a element within the current row
                        link_element = row.find_element(By.XPATH, './/td[2]/a')
                        # Get the href attribute value and append it to the array
                        href_value = link_element.get_attribute('href')
                        page = re.search(
                            r'JoOpen\("(\d+)", *"(\d+)", *"(\d+)", *"([A-Za-z]+)"\)', href_value)
                        if page:
                            journalYear, object['journalNum'], object['journalPage'], letter = page.groups(
                            )

                        id_element = row.find_element(By.XPATH, './/td[1]/a')
                        id_element_href = id_element.get_attribute("href")
                        match = re.search(r'#(\d+)', id_element_href)
                        id_number = match.group(1)
                        object['id'] = int(id_number)

                        try:
                            # Get the next four tr elements using following-sibling
                            next_four_tr_elements = row.find_elements(
                                By.XPATH, 'following-sibling::tr[position()<5]')
                            var1 = next_four_tr_elements[0].text
                            # Check if there is a match and extract the result
                            object['textType'] = law_type
                            pattern = r'رقم (\S+)'
                            match = re.search(pattern, var1)
                            if match:
                                textNumber = match.group(1)
                            else:
                                textNumber = ""
                            object['textNumber'] = textNumber

                            # Define the regular expression pattern
                            pattern = r'في (\d+ [^\s]+ \d+)'
                            # Use re.search to find the match
                            match = re.search(pattern, var1)
                            if match:
                                full_date_str = match.group(1)
                                signatureDay, signatureMonth, signatureYear = full_date_str.split(
                                )
                                try:
                                    signatureMonth = arabic_months[signatureMonth]
                                    object['signatureDate'] = signatureYear + \
                                        "-" + str(signatureMonth) + \
                                        "-" + signatureDay

                                    object['signatureDate'] = dt.fromisoformat(
                                        object['signatureDate'])
                                except KeyError:
                                    object['signatureDate'] = dt.fromisoformat(
                                        "9999-12-31")
                                    print(
                                        f"Key '{signatureMonth}' does not exist in arabic_months dictionary.")

                            object['ministry'] = next_four_tr_elements[1].text

                            date = next_four_tr_elements[2].text
                            # Define the regular expression pattern
                            pattern = r'في (.*?)،'
                            # Use re.search to find the match
                            match = re.search(pattern, date)
                            # Check if there is a match and extract the result
                            if match:
                                jornal_date_str = match.group(1)
                                journalDay, journalMonth, _ = jornal_date_str.split(
                                )
                                try:
                                    journalMonth = arabic_months[journalMonth]
                                    object['journalDate'] = journalYear + \
                                        "-" + str(journalMonth) + \
                                        "-" + journalDay

                                    object['journalDate'] = dt.fromisoformat(
                                        object['journalDate'])
                                except KeyError:
                                    object['journalDate'] = dt.fromisoformat(
                                        "9999-12-31")
                                    print(
                                        f"Key '{journalMonth}' does not exist in arabic_months dictionary.")

                            else:
                                raise ValueError(
                                    "Date pattern not found in the string")

                            object['content'] = next_four_tr_elements[3].text
                            lawTexts.append(object.copy())

                        except (ValueError, IndexError) as e:
                            # Get the next three tr elements using following-sibling
                            next_three_tr_elements = row.find_elements(
                                By.XPATH, 'following-sibling::tr[position()<4]')
                            var1 = next_three_tr_elements[0].text
                            # Check if there is a match and extract the result
                            object['textType'] = law_type
                            pattern = r'رقم (\S+)'
                            match = re.search(pattern, var1)
                            if match:
                                textNumber = match.group(1)
                            else:
                                textNumber = ""
                            object['textNumber'] = textNumber

                            # Define the regular expression pattern
                            pattern = r'في (\d+ [^\s]+ \d+)'
                            # Use re.search to find the match
                            match = re.search(pattern, var1)
                            # Check if there is a match and extract the result
                            if match:
                                full_date_str = match.group(1)
                                signatureDay, signatureMonth, signatureYear = full_date_str.split(
                                )
                                try:
                                    signatureMonth = arabic_months[signatureMonth]
                                    object['signatureDate'] = signatureYear + \
                                        "-" + str(signatureMonth) + \
                                        "-" + signatureDay

                                    object['signatureDate'] = dt.fromisoformat(
                                        object['signatureDate'])
                                except KeyError:
                                    object['signatureDate'] = dt.fromisoformat(
                                        "9999-12-31")
                                    print(
                                        f"Key '{signatureMonth}' does not exist in arabic_months dictionary.")

                            date = next_three_tr_elements[1].text
                            # Define the regular expression pattern
                            pattern = r'في (.*?)،'
                            # Use re.search to find the match
                            match = re.search(pattern, date)
                            # Check if there is a match and extract the result
                            if match:
                                jornal_date_str = match.group(1)
                                journalDay, journalMonth, _ = jornal_date_str.split(
                                )
                                try:
                                    journalMonth = arabic_months[journalMonth]
                                    object['journalDate'] = journalYear + \
                                        "-" + str(journalMonth) + \
                                        "-" + journalDay

                                    object['journalDate'] = dt.fromisoformat(
                                        object['journalDate'])
                                except KeyError:
                                    object['journalDate'] = dt.fromisoformat(
                                        "9999-12-31")
                                    print(
                                        f"Key '{journalMonth}' does not exist in arabic_months dictionary.")

                            object['ministry'] = ''
                            object['content'] = next_three_tr_elements[2].text
                            lawTexts.append(object.copy())

                    storeLawText(lawTexts)
                    file.write(
                        f"{law_type} : {len(lawTexts)} records of page {i} inserted ! \n")

                    try:
                        next_page_button = WebDriverWait(driver, 120).until(
                            EC.element_to_be_clickable(
                                (By.XPATH, '//a[@href="javascript:Sauter(\'a\',3);"]'))
                        )
                        time.sleep(10)
                        next_page_button.click()
                        i += 1

                    except TimeoutException:
                        file.write(
                            f"{law_type} :  simply the final page \n")
                        timeoutCounter += 1

                        if (number_of_pages == i):
                            finish = True
                            break

                        if (timeoutCounter == 3):
                            file.write("bug occured more 3 times \n")
                            raise TimeoutException(
                                "next page button not working")

            except TimeoutException as e:
                file.write(f"TimeoutException: {e} RETRYING... \n")
            finally:
                driver.quit()
                j += 1

            if (finish):
                break

        file.write(f"PROGRAM ENDED AFTER {j} TRIES FOR {law_type}!!! \n")


def storeLawText(lawTexts):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        for law_text in lawTexts:
            # Check if the law text already exists
            existing_law_text = session.query(LawText).get(law_text['id'])
            if existing_law_text:
                # Update existing record
                existing_law_text.text_type = law_text['textType']
                existing_law_text.text_number = law_text['textNumber']
                existing_law_text.journal_date = law_text['journalDate']
                existing_law_text.journal_num = law_text['journalNum']
                existing_law_text.journal_page = law_text['journalPage']
                existing_law_text.signature_date = law_text['signatureDate']
                existing_law_text.ministry = law_text['ministry']
                existing_law_text.content = law_text['content']
            else:
                # Insert new record
                new_law_text = LawText(
                    id=law_text['id'],
                    text_type=law_text['textType'],
                    text_number=law_text['textNumber'],
                    journal_date=law_text['journalDate'],
                    journal_num=law_text['journalNum'],
                    journal_page=law_text['journalPage'],
                    signature_date=law_text['signatureDate'],
                    ministry=law_text['ministry'],
                    content=law_text['content']
                )
                session.add(new_law_text)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error inserting/updating law text: {e}")
    finally:
        session.close()


if __name__ == '__main__':

    # Create database tables
    Base.metadata.create_all(engine)

    # Initialize ChromeOptions
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)

    # Open the website
    driver.get('https://www.joradp.dz/HAR/Index.htm')

    # Switch to the frame with src="ATitre.htm"
    driver.switch_to.frame(driver.find_element(
        By.XPATH, '//frame[@src="ATitre.htm"]'))

    # Wait for an element on the page to indicate that it's fully loaded
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, '/html/body/div/table[2]/tbody/tr/td[3]/a'))
    )

    # Now you can interact with elements inside this frame
    search_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, '/html/body/div/table[2]/tbody/tr/td[3]/a'))
    )
    search_link.click()

    # Switch back to the default content before switching to another frame
    driver.switch_to.default_content()
    # Switch to the frame with name="FnCli"
    driver.switch_to.frame(driver.find_element(
        By.XPATH, '//frame[@name="FnCli"]'))

    # Find the input field and enter '01/01/1964'
    select_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, 'znat'))
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

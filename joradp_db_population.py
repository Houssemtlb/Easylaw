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

arabic_months = {
    'يناير': 1,
    'فبراير': 2,
    'مارس': 3,
    'أبريل': 4,
    'مايو': 5,
    'يونيو': 6,
    'يوليو': 7,
    'غشت': 8,
    'سبتمبر': 9,
    'أكتوبر': 10,
    'نوفمبر': 11,
    'ديسمبر': 12
}


def scrape_law_data(law_type):
    number_of_pages = 0
    i = 0
    j = 0
    while (i <= number_of_pages):
        i = 0
        lawTexts = []
        print(f"TRY NUMBER {j + 1} FOR {law_type}!!!")
        try:
            options = Options()
            # options.add_argument("--headless=new")
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

            # select category
            select_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, 'znat')))

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

            while (i <= number_of_pages):
                matching_rows = driver.find_elements(
                    By.XPATH, '//tr[@bgcolor="#78a7b9"]')
                # Iterate through the matching rows
                with open(f'.\\pages_scraping_logs\\{law_type}\\page_{i}.txt', 'w', encoding='utf-8') as file:
                    row_number = 0
                    for row in matching_rows:
                        allAssoc = []
                        row_number += 1
                        print("row: ", row_number)
                        object = {'id': -1, 'textType': '', 'textNumber': '', 'journalYear': '', 'journalDay': '', 'journalMonth': '', 'journalNum': '',
                                  'journalPage': '', 'singatureDay': '', 'singatureMonth': '', 'singatureYear': '', 'ministry': '', 'content': ''}
                        # Find the a element within the current row
                        link_element = row.find_element(By.XPATH, './/td[2]/a')
                        # Get the href attribute value and append it to the array
                        href_value = link_element.get_attribute('href')
                        page = re.search(
                            r'JoOpen\("(\d+)", *"(\d+)", *"(\d+)", *"([A-Za-z]+)"\)', href_value)
                        if page:
                            object['journalYear'], object['journalNum'], object['journalPage'], letter = page.groups(
                            )

                        id_element = row.find_element(By.XPATH, './/td[1]/a')
                        id_element_href = id_element.get_attribute("href")
                        match = re.search(r'#(\d+)', id_element_href)
                        id_number = match.group(1)
                        object['id'] = id_number

                        next_siblings = []
                        current_element = row
                        assocObject = {"assoc": "",
                                       "idOut": object['id'], "idsIn": []}
                        sibling_number = 0
                        while True:
                            sibling_number += 1
                            print(
                                "----------------- \n Following sibling number:", sibling_number)
                            log_line = f"----------------- \n Following sibling number: {sibling_number}\n"
                            file.write(log_line)
                            following_sibling_found = current_element.find_elements(
                                By.XPATH, 'following-sibling::tr[1]')
                            try:
                                if (following_sibling_found):
                                    following_sibling = following_sibling_found[0]
                                    print(
                                        " ----------------- \n Following sibling found")
                                    log_line = f" ----------------- \n Following sibling found\n"
                                    file.write(log_line)

                                    print(
                                        f"Following sibling Text: \n {following_sibling.text}\n")
                                    log_line = f"Following sibling Text: \n {following_sibling.text}\n"
                                    file.write(log_line)

                                    sibling_bgcolor = following_sibling.get_attribute(
                                        'bgcolor')
                                    print(
                                        f"Sibling bgcolor: {sibling_bgcolor}")
                                    log_line = f"Sibling bgcolor: {sibling_bgcolor}\n"
                                    file.write(log_line)

                                    if (sibling_bgcolor == "#78a7b9"):
                                        print(
                                            "***********\n Next law found \n ***********\n**************\n")
                                        log_line = f"***********\n Next law found\n ***********\n**************\n"
                                        file.write(log_line)

                                        if (assocObject['assoc'] != ''):
                                            log_line = f"assocObject: {assocObject}\n"
                                            file.write(log_line)
                                            print("assocObject:", assocObject)

                                            allAssoc.append(assocObject)
                                            log_line = f"All law Assoc: {allAssoc}\n"
                                            file.write(log_line)
                                            print("All law Assoc:", allAssoc)

                                        break
                                    else:
                                        td_elements = following_sibling.find_elements(
                                            By.XPATH, './/td')
                                        law_td = td_elements[0]
                                        marg = law_td.get_attribute("colspan")
                                        print(f"Colspan for law_td: {marg}")
                                        log_line = f"Colspan for law_td: {marg}\n"
                                        file.write(log_line)

                                        if (marg == "6"):
                                            next_siblings.append(
                                                following_sibling)
                                            print("Added to next_siblings")
                                            log_line = f"Added to next_siblings\n"
                                            file.write(log_line)
                                        else:
                                            assoc_td = td_elements[1]
                                            marg = assoc_td.get_attribute(
                                                "colspan")
                                            log_line = f"Colspan for assoc_td: {marg}\n"
                                            file.write(log_line)
                                            print(
                                                f"Colspan for assoc_td: {marg}")

                                            if (marg == "5"):
                                                if (assocObject['assoc'] != ''):
                                                    log_line = f"assocObject: {assocObject}\n"
                                                    file.write(log_line)
                                                    print("assocObject:",
                                                          assocObject)
                                                    allAssoc.append(
                                                        assocObject)
                                                    log_line = f"All law Assoc until now: {allAssoc}\n"
                                                    file.write(log_line)
                                                    print(
                                                        "All law Assoc until now:", allAssoc)

                                                assoc = assoc_td.find_element(
                                                    By.TAG_NAME, 'font')
                                                assocObject = {
                                                    "assoc": "", "idOut": object['id'], "idsIn": []}
                                                assocObject["assoc"] = assoc.text
                                                print(
                                                    f"Association text: {assoc.text}")
                                                log_line = f"Association text: {assoc.text}\n"
                                                file.write(log_line)

                                            else:
                                                law_td = td_elements[0]
                                                marg = law_td.get_attribute(
                                                    "colspan")
                                                print(
                                                    f"Colspan for law_td (2nd check): {marg}")
                                                log_line = f"Colspan for law_td (2nd check): {marg}\n"
                                                file.write(log_line)

                                                if (marg == "2"):
                                                    if (len(td_elements) == 3):
                                                        law_td = td_elements[2]
                                                        color = law_td.get_attribute(
                                                            "bgcolor")
                                                        print(
                                                            f"Law_td bgcolor: {color}")
                                                        log_line = f"Law_td bgcolor: {color}\n"
                                                        file.write(log_line)

                                                        if (color == "#9ec7d7"):
                                                            law_td = td_elements[1]
                                                            id_element = law_td.find_element(
                                                                By.TAG_NAME, 'a')
                                                            id_element_href = id_element.get_attribute(
                                                                "href")
                                                            print(
                                                                f"Law ID href: {id_element_href}")
                                                            log_line = f"Law ID href: {id_element_href}\n"
                                                            file.write(
                                                                log_line)

                                                            match = re.search(
                                                                r'#(\d+)', id_element_href)
                                                            id_number = -1
                                                            if match:
                                                                id_number = match.group(
                                                                    1)
                                                                assocObject["idsIn"].append(
                                                                    id_number)
                                                                print(
                                                                    f"Law ID: {id_number}")
                                                                log_line = f"Law ID: {id_number}\n"
                                                                file.write(
                                                                    log_line)
                                                            else:
                                                                print(
                                                                    "Error finding law id!")
                                                                log_line = f"Error finding law id!\n"
                                                                file.write(
                                                                    log_line)

                                                        else:
                                                            print(
                                                                "Processing another law for the association")
                                                            log_line = f"Processing another law for the association\n"
                                                            file.write(
                                                                log_line)
                                                    else:
                                                        # association law data
                                                        print(
                                                            "association law data")
                                                        log_line = f"association law data\n"
                                                        file.write(log_line)
                                                else:
                                                    print(
                                                        "No matching conditions for association law")
                                                    log_line = f"No matching conditions for association law\n"
                                                    file.write(log_line)
                                else:
                                    # the last element in the page
                                    break
                            except Exception as e:
                                log_line = f"Error in processing: {e}\n"
                                file.write(log_line)
                                print(f"Error in processing: {e}")

                            current_element = following_sibling

                        print("len(next_siblings): ", len(next_siblings))
                        print("row", row_number)

                        if (len(next_siblings) == 4):
                            var1 = next_siblings[0].text
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
                                object['singatureDay'], singatureMonth, object['singatureYear'] = full_date_str.split(
                                )
                                object['singatureMonth'] = arabic_months[singatureMonth]

                            object['ministry'] = next_siblings[1].text

                            date = next_siblings[2].text
                            # Define the regular expression pattern
                            pattern = r'في (.*?)،'
                            # Use re.search to find the match
                            match = re.search(pattern, date)
                            # Check if there is a match and extract the result
                            if match:
                                jornal_date_str = match.group(1)
                                object['journalDay'], journalMonth, _ = jornal_date_str.split(
                                )
                                object['journalMonth'] = arabic_months[journalMonth]

                            object['content'] = next_siblings[3].text
                            lawTexts.append(object.copy())

                        elif (len(next_siblings) == 3):
                            var1 = next_siblings[0].text
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
                                object['singatureDay'], singatureMonth, object['singatureYear'] = full_date_str.split(
                                )
                                object['singatureMonth'] = arabic_months[singatureMonth]
                            date = next_siblings[1].text
                            # Define the regular expression pattern
                            pattern = r'في (.*?)،'
                            # Use re.search to find the match
                            match = re.search(pattern, date)
                            # Check if there is a match and extract the result
                            if match:
                                jornal_date_str = match.group(1)
                                object['journalDay'], journalMonth, _ = jornal_date_str.split(
                                )
                                object['journalMonth'] = arabic_months[journalMonth]

                            object['content'] = next_siblings[2].text
                            lawTexts.append(object.copy())
                        else:
                            print("ERROR")

                    log_line = f"~~~~~~~~~~~~~~~~ \n Following sibling number: {lawTexts}\n"
                    print(log_line)
                    file.write(log_line)

                    log_line = f"~~~~~~~~~~~~~~~~ \n Lenght: {len(lawTexts)}\n"
                    print(log_line)
                    file.write(log_line)

                next_page_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '//a[@href="javascript:Sauter(\'a\',3);"]'))
                )

                next_page_button.click()
                time.sleep(10)
                i = i + 1
                print(i)
        except TimeoutException as e:
            print(f"TimeoutException: {e} RETRYING...")
        finally:
            driver.quit()
            j += 1

    print(f"PROGRAM ENDED AFTER {j + 1} TRIES FOR {law_type}!!!")


if __name__ == '__main__':

    # Initialize ChromeOptions
    options = Options()
    # options.add_argument("--headless=new")
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

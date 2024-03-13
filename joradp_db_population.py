import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

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
number_of_pages = 0
i = 0
j = 0
while (i <= number_of_pages):
    i = 0
    lawTexts = []
    print(f"TRY NUMBER {j + 1} !!!")
    try:
        driver = webdriver.Firefox()

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

        irsal_link = WebDriverWait(driver, 10).until(
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

        number_of_pages = int(int(number_of_laws) / 200) - 1
        
        while (i <= number_of_pages):
            matching_rows = driver.find_elements(
                By.XPATH, '//tr[@bgcolor="#78a7b9"]')
            # Iterate through the matching rows
            for row in matching_rows:
                object = {'id': -1,'textType': '', 'textNumber': '', 'journalYear': '', 'journalDay': '', 'journalMonth': '', 'journalNum': '',
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
                while True:
                    assocObject = {"assoc": "", "idOut": object['id'], "idsIn": []}
                    association = ""
                    try:
                        # Attempt to find the immediately following sibling
                        following_sibling = current_element.find_element(By.XPATH, 'following-sibling::tr[1]')
                        # Check if the following sibling has the bgcolor attribute set to "#78a7b9"
                        if following_sibling.get_attribute('bgcolor') == "#78a7b9":
                            print(assocObject)
                            # If it has, we've reached the next row of interest, so stop the loop
                            break
                        try:
                            # Attempt to find the element
                            law_td = following_sibling.find_element(By.XPATH, './/td[1]')
                            marg = law_td.get_attribute("colspan")
                            if (marg == 2):
                                law_td = following_sibling.find_element(By.XPATH, './/td[3]')
                                color = law_td.get_attribute("bgcolor")
                                if (color == "#9ec7d7"):
                                    id_element = row.find_element(By.XPATH, './/td[2]/a')
                                    id_element_href = id_element.get_attribute("href")
                                    match = re.search(r'#(\d+)', id_element_href)
                                    id_number = -1
                                    if match:
                                        id_number = match.group(1)
                                        assocObject["idsIn"].append(id_number)
                        except NoSuchElementException:
                            try:
                                assocObject = {"assoc": "", "idOut": object['id'], "idsIn": []}
                                association = ""
                                assoc_td = following_sibling.find_element(By.XPATH, './/td[2]')
                                marg = assoc_td.get_attribute("colspan")
                                if (marg == "5"):
                                    assoc = following_sibling.find_element(By.XPATH, './/td[2]/font')
                                    # If the element is found
                                    association = assoc.text
                                    assocObject["assoc"] = association
                            except NoSuchElementException:
                                law_td = following_sibling.find_element(By.XPATH, './/td[1]')
                                marg = law_td.get_attribute("colspan")
                                if (marg == 6):
                                    next_siblings.append(following_sibling)
                    except NoSuchElementException:
                        # the last element in the page
                        break
                    current_element = following_sibling
                
                print(len(next_siblings))

                if(len(next_siblings) == 4):
                    var1 = next_siblings[0].text
                    # Define the regular expression pattern
                    pattern = r'في (\d+ [^\s]+ \d+)'
                    # Use re.search to find the match
                    match = re.search(pattern, var1)
                    # Check if there is a match and extract the result
                    if match:
                        full_date_str = match.group(1)
                        object['singatureDay'], singatureMonth, object['singatureYear'] = full_date_str.split()
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
                        object['journalDay'], journalMonth, _ = jornal_date_str.split()
                        object['journalMonth'] = arabic_months[journalMonth]

                    object['content'] = next_siblings[3].text
                    lawTexts.append(object.copy())

                elif (len(next_siblings) == 3):
                    var1 = next_siblings[0].text
                    # Define the regular expression pattern
                    pattern = r'في (\d+ [^\s]+ \d+)'
                    # Use re.search to find the match
                    match = re.search(pattern, var1)
                    # Check if there is a match and extract the result
                    if match:
                        full_date_str = match.group(1)
                        object['singatureDay'], singatureMonth, object['singatureYear'] = full_date_str.split()
                        object['singatureMonth'] = arabic_months[singatureMonth]
                    date = next_siblings[1].text
                    # Define the regular expression pattern
                    pattern = r'في (.*?)،'
                    # Use re.search to find the match
                    match = re.search(pattern, date)
                    # Check if there is a match and extract the result
                    if match:
                        jornal_date_str = match.group(1)
                        object['journalDay'], journalMonth, _ = jornal_date_str.split()
                        object['journalMonth'] = arabic_months[journalMonth]

                    object['content'] = next_siblings[2].text
                    lawTexts.append(object.copy())
                else:
                    print("ERROR")
#            print(lawTexts)
 #           print(len(lawTexts))
            next_page_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//a[@href="javascript:Sauter(\'a\',3);"]'))
            )
            next_page_button.click()
            time.sleep(10)
            i += 1
            print(i)
    except TimeoutException as e:
        print(f"TimeoutException: {e} RETRYING...")
    finally:
        driver.quit()
        j += 1

print(f"PROGRAM ENDED AFTER {j + 1} TRIES !!!")

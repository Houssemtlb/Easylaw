import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

arabic_months = {
    'يناير': 1,
    'فبراير': 2,
    'مارس': 3,
    'أبريل': 4,
    'مايو': 5,
    'يونيو': 6,
    'يوليو': 7,
    'أغسطس': 8,
    'سبتمبر': 9,
    'أكتوبر': 10,
    'نوفمبر': 11,
    'ديسمبر': 12
}

i = 0
j = 0
while (i <= 335):
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

        while (i <= 335):
            object = {'journalYear': '', 'journalDay': '', 'journalMonth':'', 'journalNum': '', 'journalPage': '', 'singatureDay': '', 'singatureMonth': '', 'singatureYear': '', 'ministry': '', 'content': ''}
            matching_rows = driver.find_elements(By.XPATH, '//tr[@bgcolor="#78a7b9"]')
            # Iterate through the matching rows
            for row in matching_rows:
                # Find the a element within the current row
                link_element = row.find_element(By.XPATH,'.//td[2]/a')
                # Get the href attribute value and append it to the array
                href_value = link_element.get_attribute('href')
                page = re.search(r'JoOpen\("(\d+)", *"(\d+)", *"(\d+)", *"([A-Za-z]+)"\)', href_value)
                if page:
                    object['journalYear'], object['journalNum'], object['journalPage'], letter = page.groups()

                # Get the next four tr elements using following-sibling
                next_tr_elements = row.find_elements(By.XPATH, 'following-sibling::tr[position()<5]')

                var1 = next_tr_elements[0].text
                # Define the regular expression pattern
                pattern = r'في (\d+ [^\s]+ \d+)'
                # Use re.search to find the match
                match = re.search(pattern, var1)
                # Check if there is a match and extract the result
                if match:
                    full_date_str = match.group(1)
                    object['singatureDay'], singatureMonth, object['singatureYear'] = match.groups()
                    object['singatureMonth'] = arabic_months[singatureMonth]                
                
                object['ministry'] = next_tr_elements[1].text if (len(next_tr_elements) == 4) else ''
                
                date = next_tr_elements[2 if (len(next_tr_elements) == 4) else 1].text
                # Define the regular expression pattern
                pattern = r'في (.*?)،'
                # Use re.search to find the match
                match = re.search(pattern, date)
                # Check if there is a match and extract the result
                if match:
                    jornal_date_str = match.group(1)
                    object['journalDay'], journalMonth, _ = match.groups()
                    object['journalMonth'] = arabic_months[journalMonth]
                
                object['content'] = next_tr_elements[3].text
                
                lawTexts.append(object.copy())
            print(len(lawTexts))
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
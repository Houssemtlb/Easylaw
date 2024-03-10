import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

i = 0
j = 0
while (i <= 335):
    i = 0
    print(f"TRY NUMBER {j + 1} !!!")
    try:
        driver = webdriver.Chrome()

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

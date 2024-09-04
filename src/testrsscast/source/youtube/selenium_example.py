#!/usr/bin/python3
#


# pip3 install selenium
# pip3 install webdriver-manager
# pip3 install undetected-chromedriver


import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.keys import Keys
# from webdriver_manager.chrome import ChromeDriverManager
# import undetected_chromedriver as uc


def main():
    print("starting chromium")

    # driver_path = ChromeDriverManager().install()

    # chrome_options = Options()
    # chrome_options.add_argument('--headless')
    # # driver = webdriver.Chrome(driver_path, options=chrome_options)
    # driver = uc.Chrome(options=chrome_options)
    # # driver = webdriver.Chrome(driver_path)

    driver = webdriver.Firefox()

    print("opening")
    driver.get("https://tubemp3.is/")

    print("searching item")
    elem = driver.find_element(By.ID, "u")
    elem.clear()
    elem.send_keys("https://www.youtube.com/watch?v=BLRUiVXeZKU")
    # elem.send_keys(Keys.RETURN)

    time.sleep(1)

    elem = driver.find_element(By.ID, "convert")
    elem.click()

    print("waiting for download button")
    time.sleep(1)

    elem = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn:nth-child(1)")))

    # elem = driver.find_element(By.CLASS_NAME, "start-button")
    elem.click()

    # elem = driver.find_element(By.ID, "convert1")
    # print("found button", elem)
    #
    # elem.click()

    print("download clicked")
    time.sleep(15)

    print("closing...")
    # close the driver
    driver.close()


if __name__ == '__main__':
    main()

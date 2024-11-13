import time
import re
from datetime import date

import pandas as pd
import numpy as np
import requests
import undetected_chromedriver as uc
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup



def refresh_browser(driver):
    """Refresh the webdriver"""
    driver.close()
    options = uc.ChromeOptions()
    driver = webdriver.Chrome(options=options)

    return driver


def scrape_zolo(driver, index) -> str:
    """Take the index and return the estimated price of the corresponding mls listing from zolo"""

    driver.get('https://www.zolo.ca/index.php?sarea={}&filter=1'.format(df.loc[index, 'mls_nbre']))
    try:
        WebDriverWait(driver,5).until(EC.presence_of_element_located((By.XPATH, '/html/body/main/section[2]/div/article[1]/div[1]/ul/li[1]/span[2]')))
        driver.find_element(By.XPATH, '/html/body/main/section[2]/div/article[1]/div[2]/a/img').click()
        time.sleep(1)
        driver.find_element(By.XPATH, "//*[contains(text(),'View Full Listing')]").click()
        time.sleep(1)
        try:
            est_price = driver.find_element(By.XPATH, '//*[@id="listing"]/div/div/section[7]/div/div/div[2]').text
        except:
            est_price = driver.find_element(By.XPATH, '//*[@id="listing"]/div/div/section[8]/div/div/div[2]').text
        est_price = est_price.replace('$','').replace(',','')
        if est_price == '':
            raise Exception
        
    except:
        return None
    if 'Oops!' in driver.page_source:
        return None
    try:
        int(est_price)
    except:
        return None
    
    return est_price


def scrape_hs(driver, index) -> str:
    """Take the index and return the estimated price of the corresponding mls listing from housesigma"""

    driver.get('https://housesigma.com/web/en/')
    try:
        WebDriverWait(driver,5).until(EC.presence_of_element_located((By.NAME, 'search_input'))).send_keys(df.loc[index, 'mls_nbre'])
        time.sleep(2)
        link = driver.find_element(By.CLASS_NAME, 'search_result_content').get_attribute('innerHTML')
        link = 'https://housesigma.com' + re.findall('a href="(.+?)"', link)[1]
        driver.get(link)
        time.sleep(2)
        est_price = WebDriverWait(driver,5).until(EC.presence_of_element_located((By.CLASS_NAME, 'price_dollar'))).text
        est_price = est_price.replace('$','').replace(',','')
    
    except:
        return None
    try:
        int(est_price)
    except:
        return None

    return est_price


def scrape_wahi(index) -> str: 
    """Take the index and return the estimated price of the corresponding mls listing"""

    #if df_sale.loc[index, 'Type_own1_out'] == 'Vacant Land':
    #    return

    #driver = refresh_browser(driver)
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    mls_num = df.loc[index, 'mls_nbre']
    listing_url = f'https://wahi.com/ca/en/real-estate/{mls_num}'
    driver.get(listing_url)
    time.sleep(1)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    mls_check = str(soup.find_all('td', {'class':'text-secondary-black pl-3'}))
    if mls_num not in mls_check:
        driver.close()
        return

    try:
        est_price = soup.find('div', {'class':'flex items-center w-auto'}).text.replace('$','').replace(',','').replace('*','')
    except:
        driver.close()
        return

    driver.close()

    return est_price


def main():

    global df

    df = pd.read_csv(r'C:\Users\Jordan\project\condopilot\testing_backend_sale.csv')

    options = uc.ChromeOptions()
    #options.add_argument("--headless") #Headless works on housesigma but not on zolo
    driver = webdriver.Chrome(options=options)

    for index in range(0, len(df)):
        df.loc[index, 'zolo_price'] = scrape_zolo(driver, index)
        df.loc[index, 'hs_price'] = scrape_hs(driver, index)
        df.loc[index, 'wahi_price'] = scrape_wahi(index)
    
    driver.close()

    df.to_csv(r'C:\Users\Jordan\project\condopilot\testing_backend_sale.csv', index=False)


if __name__ == "__main__":
    main()

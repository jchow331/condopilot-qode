import time
import re
from datetime import date

import pandas as pd
import numpy as np
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup

website_url = 'https://wahi.com/ca/en/real-estate/search?coordinates_latitude=43.726495&coordinates_longitude=-79.390641&active=true&listView=false'


def scrape_condos(driver) -> list:
    """Iterate through pages manually to scrape all condo urls"""

    driver.get(website_url)
    all_listings = []

    #Gets the urls and adds them to a list
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    listings = soup.find_all('a', {'role':'link'})
    listings = ['https://wahi.com' + x.get('href') for x in listings if x]
    all_listings.extend(listings)


def refresh_browser(driver):
    """Refresh the webdriver"""
    driver.close()
    options = uc.ChromeOptions()
    driver = webdriver.Chrome(options=options)

    return driver


def scrape_wahi(index) -> str: 
    """Take the index and return the estimated price of the corresponding mls listing"""

    #if df_sale.loc[index, 'Type_own1_out'] == 'Vacant Land':
    #    return

    #driver = refresh_browser(driver)
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    mls_num = df_sale.loc[index, 'mls_nbre']
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

    global df_sale

    df_sale = pd.read_csv(r'C:\Users\Jordan\project\condopilot\testing_backend_sale.csv')

    for index in range(0, len(df_sale)):
        df_sale.loc[index, 'wahi_price'] = scrape_wahi(index)



    df_sale.to_csv(r'C:\Users\Jordan\project\condopilot\testing_backend_sale.csv', index=False)


        #driver.find_element(By.XPATH, '//*[@id="__next"]/div[3]/div/div/section[1]/div[1]/div/div/div/div[1]/input').send_keys(mls_num)
        #time.sleep(2)

        #listing_url = driver.find_element(By.CLASS_NAME, 'overflow-hidden').get_attribute('innerHTML')
        #listing_url = 'https://wahi.com' + next(iter(re.findall('href="(.+?)"', listing_url)), "")



if __name__ == "__main__":
    main()

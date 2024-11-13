from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import requests
import time
import re

def scroll(driver):
    driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/section/div/div[1]/div[2]/div[2]/div/div/div[1]/div[1]/div[2]/div[1]/div[1]/span').click()
    #400 gives around 1 days worth of listings
    for scroll in range(0,600):
        body = driver.find_element(By.CSS_SELECTOR, 'body')
        body.send_keys(Keys.PAGE_DOWN)
    return

def scrape_condo(driver):
    x = 1
    all_info = []
    while True:
        try:
            try:
                driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/section/div/div[1]/div[2]/div[2]/div/div/div[1]/div[{}]/div[2]/div[1]/div[2]/p[1]'.format(x)).click()
            except:
                x+=1
                break
            time.sleep(1)
            
            #Gets fair value and decides whether to scrape or not
            try:
                fair_value = WebDriverWait(driver,5).until(EC.presence_of_element_located(
                    (By.XPATH, '/html/body/div[1]/div[2]/section/div/div[2]/section/div/div[3]/div[2]/section/div[1]/div/div[2]/div/p[2]'))).text
            except:
                continue
            fair_value = re.sub('\D','',fair_value)
            if fair_value == '':
                x+=1
                continue
            elif int(fair_value) > 3000000:
                x+=1
                continue
            
            #Scrape
            info = [None]*17
            info[0] = driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/section/div/div[1]/div[2]/div[2]/div/div/div[1]/div[{}]/div[2]/div[2]/p[1]/span[2]'.format(x)).text
            info[1] = driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/section/div/div[1]/div[2]/div[2]/div/div/div[1]/div[{}]/div[2]/div[1]/div[2]/p[1]'.format(x)).text
            info[2] = re.sub('\D','',driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/section/div/div[1]/div[2]/div[2]/div/div/div[1]/div[{}]/div[2]/div[1]/div[2]/p[2]'.format(x)).text.split(' ')[0])
            info[3] = int(fair_value)
            try:
                info[6] = driver.find_element(By.CLASS_NAME, 'bed').text
                info[6] = re.sub('\D','',info[6])
            except:
                pass
            try:
                info[7] = driver.find_element(By.CLASS_NAME, 'bath').text
                info[7] = re.sub('\D','',info[7])
            except:
                pass
            try:
                info[8] = driver.find_element(By.CLASS_NAME, 'gar').text
                info[8] = re.sub('\D','',info[8])
            except:
                pass
            try:
                info[9] = driver.find_element(By.CLASS_NAME, 'sqft').text
            except:
                pass
            features = driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/section/div/div[2]/section/div/div[3]/div[2]/section/div[1]/div/div[1]/div[2]/div[2]/div').text
            features = features.split('\n')
            try:
                info[11] = features[features.index('Age of building') + 1]
            except:
                pass
            try:
                info[10] = features[features.index('Price per ft2') + 1]
            except:
                pass
            try:
                info[12] = features[features.index('Maintenance fees') + 1]
            except:
                pass
            try:
                info[13] = features[features.index('Possession') + 1]
            except:
                pass
            try:
                info[14] = features[features.index('Outdoor space') + 1]
            except:
                pass
            try:
                info[15] = features[features.index('Locker') + 1]
            except:
                pass
            labels = driver.find_elements(By.CLASS_NAME, 'property_label_v2')
            labels = [x.text for x in labels]
            values = driver.find_elements(By.CLASS_NAME, 'property_value_v2')
            values = [x.text for x in values]
            try:
                info[16] = values[labels.index('Property type')]
            except:
                pass
            
            all_info.append(info)
            x+=1
            time.sleep(0.5)
        except:
            continue
        
    return all_info

def scrape_zolo(driver, x):
    driver.get('https://www.zolo.ca/index.php?sarea={}&filter=1'.format(all_info[x][0]))
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
        return '0'
    if 'Oops!' in driver.page_source:
        return '0'
    
    return est_price

def scrape_hs(driver, x):
    driver.get('https://housesigma.com/web/en/')
    try:
        WebDriverWait(driver,5).until(EC.presence_of_element_located((By.NAME, 'search_input'))).send_keys(all_info[x][0])
        #WebDriverWait(driver,5).until(EC.presence_of_element_located((By.NAME, 'search_input'))).send_keys(x)
        time.sleep(2)
        link = driver.find_element(By.CLASS_NAME, 'search_result_content').get_attribute('innerHTML')
        link = 'https://housesigma.com' + re.findall('a href="(.+?)"', link)[1]
        driver.get(link)
        time.sleep(2)
        est_price = WebDriverWait(driver,5).until(EC.presence_of_element_located((By.CLASS_NAME, 'price_dollar'))).text
        est_price = est_price.replace('$','').replace(',','')
    
    except:
        return '0'
    return est_price
    

if __name__ == "__main__":


    df = pd.read_csv(r'C:\Users\Jordan\project\condopilottesting_backend_sale.csv')
      
    options = Options()
    options.binary_location = "C:/Program Files/Google/Chrome Beta/Application/chrome.exe"
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    driver.get('https://condopilot.ca/map-list?type=Sale&q=toronto')
    time.sleep(5)
    
    #Scroll
    scroll(driver)
    
    #Scrape condopilot data
    all_info = scrape_condo(driver)
    
    #for x in range(len(all_info)):
    for x in range(0,5):
        
        #Scrape zolo data
        all_info[x][4] = int(re.sub('\D','', scrape_zolo(driver,x)))
        
        #Scrape housesigma data
        all_info[x][5] = int(re.sub('\D','', scrape_hs(driver,x)))
        
# =============================================================================
#     #Try to get the missing zolo stuff?
#     for x in df.loc[df['zolo_value'].isnull()].index.values:
#         all_info[x][4] = int(re.sub('\D','', scrape_zolo(driver,x)))
# =============================================================================
    

    df = pd.concat([df, (pd.DataFrame(all_info, columns=df.columns))])
    df['zolo_value'] = df['zolo_value'].replace({0:None})
    df = df.loc[df['zolo_value'] != 3]
    #df = df.dropna(subset=['zolo_value'])
    df = df.drop_duplicates(subset=['MLS'], keep='last')
    df.to_csv(r'C:\Users\Jordan\project\condopilot\testing_backend_sale.csv', index=False)

#Line Item readout - AQA_Tool 2.8.2

import getpass

import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import datetime

from bs4 import BeautifulSoup
import re
import json

now = datetime.datetime.now()
df = pd.DataFrame()

#--------------------------------Functions--------------------------------
def getSetting():
    pg = driver.page_source
    soup = BeautifulSoup(pg,'lxml')
    title = soup.findAll('title')[0].string
    lineItem = str(title).replace('Line item: ','')
    
    for settings in soup.findAll('script'):
        if settings.string is None:
            continue
        formatSettings = re.search('summaryViewModel = (.+?)\n', settings.string)
        if formatSettings is not None:
            data = [formatSettings.group(1)[:-1],lineItem]
            return data
          
    return lineItem

def getKeyValue(listed, category, key):
    for outerList in listed:
        for dictionary in outerList:
                if dictionary.get('keyLabel') == category:
                    return dictionary.get(key)

def checkList(data):
    if data is None:
        data = ['Check in Rodeo']
    else:
        data = [', '.join(data)]
    return data

def checkTargetingString(content, category):
    modalText = getKeyValue(content, category, 'modalText')
    valueLabel = getKeyValue(content, category, 'valueLabel')
    
    if '...' in valueLabel:    
        return modalText
    
    return valueLabel
    

def mapContent(data):
    global df
    if data is str:
        row_data = pd.DataFrame({
            'Order Name': 'Rodeo did not properly load for',\
            'Line Item Name': data
            })
        df = df.append(row_data)
        return
    else:        
        flatten_data = json.loads(data[0])
        header = flatten_data.get('header')
        content = flatten_data.get('content')
        
        supply_source = checkList(getKeyValue(content, 'Supply sources', 'modalText'))
        product_category = checkList(getKeyValue(content,'Product categories', 'modalText'))
        
        row_data = pd.DataFrame({
                'Order Name': [getKeyValue(content, 'Order', 'entityName')],\
                'Order ID': internal_order_id,\
                'Line Item Name': [data[1]],\
                'Amazon Line Item ID': [getKeyValue(content, 'Amazon line item ID','valueLabel')],\
                'Internal Ad ID': [getKeyValue(content, 'Internal ad ID', 'valueLabel')],\
                'Flight Date': [getKeyValue(content, 'Flight dates and time', 'valueLabel')],\
                'Line Item Type': [getKeyValue(header,'Line item type', 'valueLabel')],\
                'Product Category': product_category,\
                'Frequency Cap': [getKeyValue(content, 'Frequency cap', 'valueLabel')],\
                'User Location': [getKeyValue(content, 'User location', 'valueLabel')],\
                'Supply Sources': supply_source,\
                'Final Targeting String': checkTargetingString(content, 'Text targeting string'),\
                'Video Initiation Type': [getKeyValue(content, 'Video initiation type', 'valueLabel')],\
                'Video Ad Format': [getKeyValue(content, 'Video ad format', 'valueLabel')],\
                'Domain Targeting': [getKeyValue(content, 'Domain targeting', 'message')],\
                'Site Language': [getKeyValue(content, 'Site language', 'valueLabel')],\
                'Use Daypart Targeting': [getKeyValue(content, 'Daypart targeting','valueLabel')],\
                'Content Categories': [getKeyValue(content, 'Content categories','valueLabel')],\
                'Line Item Budget': [getKeyValue(content, 'Line item budget', 'valueLabel')],\
                'Budget Cap': [getKeyValue(content, 'Budget cap', 'valueLabel')],\
                'In-market/Lifestyle Audience Fee': [getKeyValue(content, 'In-market and lifestyle segments audience fee', 'valueLabel')],\
                'Automative Audience Fee': [getKeyValue(content, 'Automotive audience fee', 'valueLabel')],\
                'Sold CPM': [getKeyValue(content, 'Sold CPM', 'valueLabel')],\
                'Min Bid': [getKeyValue(content, 'Min bid CPM', 'valueLabel')],\
                'Base Supply Bid': [getKeyValue(content, 'Base supply bid', 'valueLabel')],\
                'Max Supply Bid': [getKeyValue(content, 'Max supply bid', 'valueLabel')],\
                'Optimization': [getKeyValue(content, 'Optimization type', 'valueLabel')]
                })
        df = df.append(row_data)
        return

def loadextendedlines(lines):
    driver.find_element_by_xpath('//*[@id="wc-lineItemsTable"]/section/div/article[2]/div[3]/span/span/span/span').click()
    driver.find_element_by_xpath('//*[@id="dropdown1_3"]').click()
    if int(lines) > 500:
        WebDriverWait(driver, 180).until(
        EC.text_to_be_present_in_element((By.XPATH,'//*[@id="wc-lineItemsTable"]/section/div/article[2]/div[2]/ul/li[1]'), "1-500"))
        print('Expanded lines to full list of MAX 500 lines...')
    else:
        WebDriverWait(driver, 180).until(
        EC.text_to_be_present_in_element((By.XPATH,'//*[@id="wc-lineItemsTable"]/section/div/article[2]/div[3]/ul/li[1]'), lines))
        print('Expanded lines to full list of ' + str(lines) + ' lines...')
    

def linknotpresent(text):
    while False:
        try:
            driver.find_element_by_link_text(text)
            return True
        except NoSuchElementException:
            return False

def pathnotpresent(text):
    while False:
        try:
            driver.find_element_by_xpath(text)
            return True
        except NoSuchElementException:
            return False

def idnotpresent(text):
    while False:
        try:
            driver.find_element_by_id(text)
            return True
        except NoSuchElementException:
            return False

#--------------------------------Script--------------------------------

#take inputs, ingress to Rodeo
url = input('What is the Rodeo order URL? ')
orderid = url[url.find('orders/')+7:url.find('/line-items')]
csvname = 'xDAL_orderid' + orderid + '_' + str(now.month) + '_' + str(now.day)
csvnewname = input('Input customized output name or leave blank for default name: "'+ csvname + '": ')
if csvnewname:
    csvname = csvnewname
rodeo_username = input("USERNAME: ")
rodeo_password = getpass.getpass("PASSWORD: ")

driver = webdriver.Chrome()
driver.implicitly_wait(30)
driver.maximize_window()
print ('Logging into Rodeo and visualizing Order...')
driver.get(url)
driver.find_element_by_xpath("//*[@id='ap_email']").send_keys(rodeo_username)
driver.find_element_by_xpath("//*[@id='ap_password']").send_keys(rodeo_password)
driver.find_element_by_xpath("//*[@id='signInSubmit']").click()
internal_order_id = driver.find_element_by_xpath("//*[@id='page-header-metadata__internalOrderId']").text.replace("Internal campaign ID:","")

#show 500 orders per page
lines = driver.find_element_by_xpath('//*[@id="wc-lineItemsTable"]/section/div/article[2]/div[3]/ul/li[3]').text
if int(lines)> 50:
    print('Greater than 50 lines, expanding to ' + str(lines) + '...')
    loadextendedlines(lines)

#ingest list of current lines under order
adlinelist = driver.find_elements_by_xpath("//*[@id='wc-lineItemsTable']/section/div/article[1]/table/tbody/tr")
adlinestodupe = {}
for idx, val in enumerate(adlinelist):
    linelink = driver.find_element_by_xpath("//*[@id='wc-lineItemsTable']/section/div/article[1]/table/tbody/tr[" + str(idx+1) + "]/td[5]/div/div/div/a").text
    linespend = driver.find_element_by_xpath("//*[@id='wc-lineItemsTable']/section/div/article[1]/table/tbody/tr[" + str(idx+1) + "]/td[8]/div").text.replace('Ã¢â‚¬â€','0') #no longer needed
    adlinestodupe[linelink] = linespend
length = str(len(adlinestodupe))
print ('Completed getting line list of ' + length + ' lines...')

#get ad line data
driver.execute_script("window.open('');")
for idx, val in enumerate(adlinestodupe):
    if linknotpresent(val):
        loadextendedlines(lines)    
    lineurl = driver.find_element_by_link_text(val).get_attribute('href')
    driver.switch_to.window(driver.window_handles[1])
    driver.get(lineurl)
    mapContent(getSetting())

    driver.switch_to.window(driver.window_handles[0])

    print("Completed getting details of line " + str(idx+1) + " of " + length + '...')
    
driver.quit()

#generate CSV output
column_order = ['Order Name', 'Order ID', 'Line Item Name', 'Amazon Line Item ID', 'Internal Ad ID', 'Flight Date','Line Item Type','Product Category',
                'Frequency Cap','User Location', 'Supply Sources','Final Targeting String',
                'Video Initiation Type','Video Ad Format', 'Domain Targeting', 'Site Language','Use Daypart Targeting',
                'Content Categories','Line Item Budget','Budget Cap','In-market/Lifestyle Audience Fee','Automative Audience Fee',
                'Sold CPM','Min Bid','Base Supply Bid','Max Supply Bid','Optimization']
df.to_csv(csvname + '.csv', columns = column_order, mode='a', index=False)
print("Completed csv save...")
print ("Complete")
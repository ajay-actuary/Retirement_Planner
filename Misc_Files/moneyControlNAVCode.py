## needs gecko driver (sudo pacman -S geckodriver)
## needs selenium (sudo pip install selenium)

# Import libraries

import time
from selenium import webdriver
import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime
import os
import openpyxl
import numpy as np

# Inputs
exportPath = '/home/ajay/Documents/Actuarial/2020_RM_Project/NAV_Data.xlsx'
outlierQntCutoff = 4 # cut off figure using n * quantile method

# Get List of Pension Funds
index_page = requests.get('https://www.moneycontrol.com/personal-finance/nps-national-pension-scheme')
soup = BeautifulSoup(index_page.text, 'html.parser')

# Pull all text from the Body
stock_name = soup.find(class_='mctable1')

# Find Pension Funds Links
stock_href = []
for a in stock_name.find_all('a', href=True):
    stock_href += [[a['href'].split('/')[5], a['href']]]

# Testing
#stock_href = stock_href[:2] ## for testing purposes
#stock_href = [['SM003010','https://www.moneycontrol.com/nps/nav/lic-pension-fund-scheme-g-tier-ii/SM003010']]

Final_DF = 0
counter = 0

for name, website in stock_href:

    driver = webdriver.Firefox()
    driver.get(website)
    
    # Select 5 year graph
    driver.find_element_by_id("li_all").click()
    time.sleep(2)
#    driver.execute_script("get_stock_graph('','5Y','li_5y','fiveymfd_5')")
    
    time.sleep(2)
    temp = driver.execute_script('return window.Highcharts.charts[window.Highcharts.charts.length-1].series[0].options.data')
    
    # Benchmark
#    temp1 = driver.execute_script('return window.Highcharts.charts[2].series[1].options.data')
    
    # Get Relevant Data & Close Driver
    df = pd.DataFrame(temp, columns = ['Date', 'Returns'])  
    df['Name'] = name
    driver.close()
    
    try:
        if Final_DF == 0:
            Final_DF = df
    except:
        Final_DF = Final_DF.append([df]).reset_index(drop=True)
    
    # Track Progress
    counter = counter+1
    print(''' {0} out of {1} completed '''.format(counter,len(stock_href)))
    
# Convert dates to human readable format
Final_DF['Date'] = Final_DF['Date'].apply(lambda x: datetime.date(1970,1,1) \
        + datetime.timedelta(days=(x/(3600*1000*24))))

# Remove redundant data
Final_DF1 = Final_DF.copy()
Final_DF1['Lag'] = Final_DF1.groupby('Name')['Returns'].shift(1)
Final_DF1 = Final_DF1.loc[(Final_DF1['Lag'] != Final_DF1['Returns']),:].dropna()

# Calculate NAV for Rs.1
Final_DF1['NAV'] = (1+Final_DF1['Returns']/100)
Final_DF1 = Final_DF1[['Name','Date','NAV']].reset_index(drop=True)

# Standardize NAV to 1 at start
firstValue = Final_DF1.groupby('Name').first()
firstValue = firstValue.reset_index()
firstValue = firstValue[['Name','NAV']]
firstValue.rename(columns={'NAV': 'First_NAV'}, inplace=True)

Final_DF1 = pd.merge(Final_DF1, firstValue, on=['Name'],how='left')
Final_DF1['NAV'] = Final_DF1['NAV']/Final_DF1['First_NAV']
Final_DF1 = Final_DF1[['Name','Date','NAV']].reset_index(drop=True)

# Calculate Returns
Final_DF1['NAV_Lag'] = Final_DF1.groupby('Name')['NAV'].shift(1).fillna(1)
Final_DF1['Returns'] = (Final_DF1['NAV']/Final_DF1['NAV_Lag'])-1

# Remove Outliers by Group Using Multiple of Quantiles Method
# Looped over twice to filter residual outliers

for x in range(2):
    q1Val = Final_DF1.groupby('Name')['Returns'].quantile(.05).reset_index()
    q3Val = Final_DF1.groupby('Name')['Returns'].quantile(.95).reset_index()
    
    q1Val.rename(columns={'Returns': 'q1'}, inplace=True)
    q3Val.rename(columns={'Returns': 'q3'}, inplace=True)
    
    Final_DF1 = pd.merge(Final_DF1, q1Val, on=['Name'],how='left')
    Final_DF1 = pd.merge(Final_DF1, q3Val, on=['Name'],how='left')
    
    Final_DF1 = Final_DF1.loc[(Final_DF1['q1']*outlierQntCutoff < Final_DF1['Returns'])  \
                 & (Final_DF1['Returns'] < Final_DF1['q3']*outlierQntCutoff),:]
    
    # Recompute Returns with Outliers Removed
    Final_DF1 = Final_DF1[['Name','Date','NAV']].reset_index(drop=True)
    Final_DF1['NAV_Lag'] = Final_DF1.groupby('Name')['NAV'].shift(1).fillna(1)
    Final_DF1['Returns'] = (Final_DF1['NAV']/Final_DF1['NAV_Lag'])-1
    Final_DF1 = Final_DF1[['Name','Date','NAV','Returns']].reset_index(drop=True)


# Remove small schemes with less than 500 data points
countVal = Final_DF1.groupby('Name')['Returns'].size().reset_index()
countVal.rename(columns={'Returns': 'Size'}, inplace=True)
Final_DF1_Reduced = pd.merge(Final_DF1, countVal, on=['Name'],how='left')
Final_DF1_Reduced = Final_DF1_Reduced.loc[Final_DF1_Reduced['Size'] > 500 ,:]
Final_DF1_Reduced = Final_DF1_Reduced[['Name','Date','Returns']].reset_index(drop=True)

# Remove days not in Monday - Friday
Final_DF1_Reduced = Final_DF1_Reduced.loc[Final_DF1_Reduced['Date'].apply(lambda x: x.weekday()) < 5,:]

# Export to Excel
Final_DF1_Reduced.to_excel(exportPath,index=False)

#################################### Correlation ###################################
Final_DF2 = Final_DF1_Reduced.pivot_table(values='Returns', index='Date', columns='Name', aggfunc='first')

pearsoncorr = Final_DF2.corr(method='pearson')

writer = pd.ExcelWriter(exportPath, engine='openpyxl')

if os.path.exists(exportPath):
    book = openpyxl.load_workbook(exportPath)
    writer.book = book

pearsoncorr.to_excel(writer, sheet_name='Correlation')
writer.save()
writer.close()
Final_DF2 = Final_DF2.reset_index()

################################### Mean & StdDev ###################################
# Find no of days in 2019 & extrapolate annualized returns

statData = Final_DF1.groupby('Name')['Returns'].agg({"returns": [np.mean, np.std]})
statData = statData.droplevel(0, axis=1) 
statData.reset_index(inplace=True)


Ann_Days = Final_DF1_Reduced.loc[Final_DF1_Reduced['Date'].apply(lambda x: x.year) == 2019,:]
Ann_Days = Ann_Days.groupby('Name').size().reset_index()
Ann_Days.rename(columns={0: '2019_Days'}, inplace=True)
statData = pd.merge(statData, Ann_Days, on=['Name'],how='left')

statData['Mean_Annualized'] = statData['mean']*statData['2019_Days']
statData['StDev_Annualized'] = statData['std']*(statData['2019_Days']**.5)

if os.path.exists(exportPath):
    book = openpyxl.load_workbook(exportPath)
    writer.book = book

statData.to_excel(writer, sheet_name='Mean_Std',index=False)
writer.save()
writer.close()


######################################################################################################
## Test code

#website = 'https://www.moneycontrol.com/nps/nav/lic-pension-fund-scheme-g-tier-ii/SM003010'
#driver = webdriver.Firefox()
#driver.get(website)
#time.sleep(2)
#driver.find_element_by_id("li_5y").click()
##driver.execute_script("get_stock_graph('','5Y','li_5y','fiveymfd_5')")
#time.sleep(2)
#temp = driver.execute_script('return window.Highcharts.charts[window.Highcharts.charts.length-1].series[0].options.data')

#temp = driver.execute_script(''' get_stock_graph('','5Y','li_5y','fiveymfd_5', schemename, 'nps'); ''')

#driver.close()
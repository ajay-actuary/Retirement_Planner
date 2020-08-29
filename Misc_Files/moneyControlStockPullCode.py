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


# Test code

website = 'https://www.moneycontrol.com/india/stockpricequote/infrastructure-general/larsentoubro/LT'
driver = webdriver.Firefox()
driver.get(website)
time.sleep(2)
driver.find_element_by_id("li_all").click()
#driver.execute_script("get_stock_graph('','5Y','li_5y','fiveymfd_5')")
time.sleep(2)
temp = driver.execute_script('return window.Highcharts.charts[window.Highcharts.charts.length-1].series[0].options.data')

driver.close()
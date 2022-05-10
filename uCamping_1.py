# todo, site is close

# you need to download, unzip and put the chromedriver.exe 
# in same folder of this py file 
# from the  https://chromedriver.chromium.org/downloads 

from __future__ import print_function
import os
import socket
import time
from matplotlib.style import available
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities \
    import DesiredCapabilities
import pandas as pd
import numpy as np
import csv
import datetime
# weekdays as a tuple
weekdays = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
# 設置超時
socket.setdefaulttimeout(10)

debugSiteID = 0
# debugSiteID = 228

USER_AGENT = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
HEADERS = {'User-Agent': USER_AGENT}

opt = webdriver.ChromeOptions()  # 创建浏览器
# opt.set_headless()                            #无窗口模式
opt.add_argument('--headless')

caps = DesiredCapabilities().CHROME
caps["pageLoadStrategy"] = "normal"  #  Waits for full page load
# caps["pageLoadStrategy"] = "none"  # Do not wait for full page load

# main function
if __name__ == "__main__":
    browser = webdriver.Chrome(desired_capabilities=caps, options=opt)  # 创建浏览器对象
    # get nowTimeStamp
    nowDateTimeYMdHMS = time.strftime("%Y%m%d%H%M%S", time.localtime())
    nowDateTimeYMd = time.strftime("%Y%m%d", time.localtime())
    csvFileName='campingSite1_'+nowDateTimeYMdHMS+'.csv'
    csvFileName='campingSite1_'+nowDateTimeYMd+'.csv'
   
    # get this month in m/1/yyyy format
    TheDate = time.strftime("%m/1/%Y")
    # get date after 6 weeks in m/d/yyyy format
    ArriveDate = time.strftime("%m/%d/%Y"\
        , time.localtime(time.time() + 6 * 7 * 24 * 3600))
    DepartDate = time.strftime("%m/%d/%Y"\
        , time.localtime(time.time() + (6 * 7 + 1 )* 24 * 3600))
    
    if debugSiteID>0:
        maxCSVSiteID=debugSiteID
        endSiteID=debugSiteID+1
    else:
        # file exists?
        maxCSVSiteID=117
        endSiteID=510
        if os.path.exists(csvFileName):
            # load csv file
            colList=['siteID', 'parkName', 'siteNumText', 'siteTypeText'\
                    ,'today','thisYear','month','availableFriSat','availableOtherDays']
            df = pd.read_csv(csvFileName, encoding='utf-8', names=colList, header=None)
            if df.shape[0]>0:
                # get the max of siteID 
                maxCSVSiteID = max(df['siteID'])

    # loop for all siteID from 117 to 510
    for siteID in range(maxCSVSiteID, endSiteID):
        # get the string of siteID
        siteIDStr = str(siteID)
        # get queryLink
        queryLink=u'https://1.org/reservations/SiteDetails.asp'\
                    +u'?SiteID='+ siteIDStr \
                        +u'&ArriveDate='+ArriveDate \
                            + u'&DepartDate='+DepartDate \
                                + u'&TheDate='+TheDate \
                                    + u'#avail'
        # Open a new window
        browser.execute_script("window.open('');")
        # Switch to the new window and open URL B
        browser.switch_to.window(browser.window_handles[-1])

        nowDateTimeYMdHMS = time.strftime("%Y%m%d%H%M%S", time.localtime())
        browser.get(queryLink)  # 打开网页
        # browser.maximize_window()                      #最大化窗口
        # if found class="alert_box_style" then click the button of "close"
        alert_box = browser.find_element_by_class_name('alert_box_style')
        if alert_box is not None:
            #find href of "javascript:close_gen_alert()"
            close_button = alert_box.find_element_by_xpath(\
                ".//a[@href='javascript:close_gen_alert()']")
            if close_button is not None:
                try:
                    close_button.click()
                except:
                    print(siteIDStr+u'close_button.click() error')
                    continue
        # find the table with class="pageTitle"
        siteTable = browser.find_element_by_xpath(\
            ".//table[contains(.,'Site:')]")
        if siteTable is not None:
            # find the text of pageTitle
            siteTableText = siteTable.text
            # find the index of "Site:"
            backToMapIndex = siteTableText.find("Back to Map")
            parkName=siteTableText[0:backToMapIndex-1]
            siteNumIndex = siteTableText.find('Site:')+len('Site:')
            siteNumIndexEnd = siteTableText.find('\n',siteNumIndex)
            siteNumText = siteTableText[siteNumIndex:siteNumIndexEnd]
            siteTypeIndex=    siteTableText.find('Site Type:')+len('Site Type:')
            siteTypeIndexEnd=    siteTableText.find('\n',siteTypeIndex)
            siteTypeText = siteTableText[siteTypeIndex:siteTypeIndexEnd]
        # find 3 month table
        monthTables=browser.find_elements_by_xpath(\
            ".//td[@bgcolor='#000000']")
        # loop over all 3 month table
        for monthTable in monthTables:
            monthYearTextEnd = monthTable.text.find('\n')
            monthYearText=monthTable.text[0:monthYearTextEnd]
            availableAll=[]
            availableAll = monthTable.find_elements_by_xpath(\
                ".//td[@bgcolor='#FFFFFF']")
            availableList=['']* (len(availableAll))
            availableListFS=['']* (len(availableAll))
            idx=0
            idxFS=0
            # loop over the availableAll
            for available in availableAll:
                if available.text!='':
                    # get the week day of a date
                    weekDay = datetime.datetime.strptime\
                        (monthYearText+' '+available.text, '%B %Y %d')\
                        .weekday()
                    # if the week day is not 0,6, then it is available
                    if weekDay==4 or weekDay==5:
                        availableListFS[idxFS]=available.text+weekdays[weekDay]
                        idxFS+=1
                    else:
                        availableList[idx]=available.text+weekdays[weekDay]
                        idx+=1
            availableList=availableList[0:idx]
            availableListFS=availableListFS[0:idxFS]
            with open(csvFileName, 'a') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([siteID, parkName, siteNumText, siteTypeText\
                                ,nowDateTimeYMdHMS\
                                ,monthYearText,availableListFS,availableList])
            pass

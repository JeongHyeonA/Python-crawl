# #!/usr/bin/python
# -*- coding : utf-8 -*-
'''
 @author : wsw
'''
''' install '''
# !pip install selenium
from operator import truediv
import time
import os
import pandas as pd
import math
import re
from selenium import webdriver
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
import platform
from logging.config import dictConfig
import logging
import warnings
import inspect
import datetime
import traceback
import sys


def log(msg):
    logging.info(msg)
class LoopBreak(Exception):
    pass

# 로그파일 생성 
filePath, fileName = os.path.split(__file__)
logFolder = os.path.join(filePath , 'logs')
os.makedirs(logFolder, exist_ok = True)
logfilepath = os.path.join(logFolder, fileName.split('.')[0] + '_' +re.sub('-', '', str(datetime.date.today())) + '.log')

dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s --- %(message)s',
        }
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': logfilepath,
            'formatter': 'default',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file']
    }
})       
      
def main():
    date, route= make_df(filePath)
    download_path = os.path.join(filePath, 'data'
)
    # 다운로드 경로 지정
    os.makedirs(download_path, exist_ok = True)
    # 드라이버 시작
    if platform.system() == 'Windows':
        driver_path = os.path.join(filePath,'chromedriver.exe')
        
    url = 'https://www.stcis.go.kr/pivotIndi/wpsPivotIndicator.do?siteGb=P&indiClss=IC03'
    driver = start_driver(driver_path, url, download_path)
    
    # 초기 세팅(38개 노선)
    first_setting(driver, route)
    for index_date in date.index:
        try :
            startdate = str(date.loc[index_date,'조회시작일'])
            startyear = str(date.loc[index_date,'startyear'])
            startmonth = str(date.loc[index_date,'startmonth'])
            startday = str(date.loc[index_date,'startday'])
            # 노선별 차내 재차인원 클릭    
            click_by_xpath(driver, '/html/body/div[1]/div[2]/form/div[3]/div[2]/div[1]/ul/li[2]')
            explicit_wait(driver, '/html/body/div[1]/div[2]/form/div[3]/div[2]/div[1]/ul/li[4]')
            ############## 조회시작일 ######################
            log('\n')
            log('#### Select Start Date')
            select_calender_date(driver, '/html/body/div[1]/div[2]/form/div[3]/div[2]/div[2]/div[1]/ul/li[1]/div/div/ul[3]/li[1]/img', startyear, startmonth, startday)
            # 검색 결과 조회 누르기
            click_by_xpath(driver, '/html/body/div[1]/div[2]/form/div[3]/div[2]/div[2]/div[1]/ul/li[3]/div[2]/button')
            # 데이터가 많아 오래걸린다고 하면 확인 누르기
            alarm_accept(driver)
            # 로딩 대기
            wait_loading(driver, '/html/body/div[5]/img')
            # ################### 다운로드 및 리네임 ###################################
            download_check(driver, download_path)
            # 리네임
            if len(startmonth) < 2 :
                startmonth = '0' + startmonth
            if len(startday) < 2 :
                startday = '0' + startday
            rename_filename = f"노선별차내재차인원_{startyear}{startmonth}{startday}.csv"
            rename_file(download_path, rename_filename)
            # 뒤로 가기
            click_by_xpath(driver, '/html/body/div[1]/div[2]/form/div[3]/div[2]/div[2]/div[2]/div[3]/button')
            log(f'\n################################# Complete All Process {rename_filename}')
        except :
            log(f'\n################################# Error : All Process')
            pass
    driver.close()
'''Functions'''
# 해당 컨텐츠가 안보일 때 까지
def wait_loading(driver, xpath):
    try:
        WebDriverWait(driver, 1200).until(EC.invisibility_of_element((By.XPATH, xpath)))
    except:
        pass
    
# 알림
def alarm_accept(driver):
    try:
        da = Alert(driver)
        da.accept()
    except:
        pass
    
# 드라이버 시작    
def start_driver(driver_path, url, down_path = None):
    try:
        log('\n#### Start Driver')
        chrome_options = webdriver.ChromeOptions()
        # 서버 전용 옵션 활성화
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--window-size=1920x1080')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        # 다운로드 경로 변경 및 기타 옵션 설정
        if down_path == None:
            prefs = {
                'download.prompt_for_download': False,
                'download.directory_upgrade': True
                }
            chrome_options.add_experimental_option('prefs', prefs)
        else:
            prefs = {
                'download.default_directory': down_path,
                'download.prompt_for_download': False,
                'download.directory_upgrade': True,
                'safebrowsing.enabled': True
                }
            chrome_options.add_experimental_option('prefs', prefs)
        # 드라이브 시작
        driver = webdriver.Chrome(service = Service(driver_path), options = chrome_options)
        driver.implicitly_wait(100) # 대기 시작 설정
        driver.get(url) # URL 적용
        # 로딩 대기
        return driver
    except:
        log('######################## Error : start_driver')
        log(traceback.format_exc())
        pass
    
def first_setting(driver, route):
    for index_route in route.index:
        place = str(route.loc[index_route,'시도명'])
        way = str(route.loc[index_route, '노선명_검색'])
        waytext = str(route.loc[index_route,'기종점'])
        waytext2 = str(route.loc[index_route,'노선명'])
        # 노선별 차내 재차인원 클릭    
        click_by_xpath(driver, '/html/body/div[1]/div[2]/form/div[3]/div[2]/div[1]/ul/li[2]')
        explicit_wait(driver, '/html/body/div[1]/div[2]/form/div[3]/div[2]/div[1]/ul/li[4]')
        ############## 조회시작일 ######################
        log('\n')
        log('#### Select Start Date')
        select_calender_date(driver, '/html/body/div[1]/div[2]/form/div[3]/div[2]/div[2]/div[1]/ul/li[1]/div/div/ul[3]/li[1]/img', 2022, 1, 28)
        ############## 시, 도 선택 #####################
        time.sleep(0.5)
        # 시,도
        click_by_xpath(driver, '/html/body/div[1]/div[2]/form/div[3]/div[2]/div[2]/div[1]/ul/li[2]/div/div[2]/ul[1]/li[1]')
        explicit_wait(driver, '/html/body/div[1]/div[2]/form/div[3]/div[2]/div[2]/div[1]/ul/li[2]/div/div[2]/ul[2]/li[2]/select')
        # 시,도 선택
        click_by_xpath(driver, '/html/body/div[1]/div[2]/form/div[3]/div[2]/div[2]/div[1]/ul/li[2]/div/div[2]/ul[2]/li[2]/select')
        # 특정 시,도 선택
        select_city(driver, place)
        ############## 노선명 선택 #####################
        time.sleep(0.5)
        # 노선명 선택 및 텍스트 입력
        click_by_xpath(driver, '/html/body/div[1]/div[2]/form/div[3]/div[2]/div[2]/div[1]/ul/li[3]/div/ul/li[1]/input').clear()
        click_by_xpath(driver, '/html/body/div[1]/div[2]/form/div[3]/div[2]/div[2]/div[1]/ul/li[3]/div[1]/ul/li[1]/input').send_keys(way)
        log('#### Input Route')
        # 검색 클릭
        click_by_xpath(driver, '/html/body/div[1]/div[2]/form/div[3]/div[2]/div[2]/div[1]/ul/li[3]/div/ul/li[1]/button')
        log('#### Search Route')
        # 노선 선택창 팝업창 로딩 이미지 사라질 때 까지 대기
        wait_loading(driver, '/html/body/div[5]/img')
        # 팝업 뜨면 선택창(노선 고르기)
        if select_way(driver, waytext, waytext2) == False:
            log(f'######################## Error : Search failed {place}, {waytext2}, {waytext}')
            click_by_xpath(driver,'/html/body/div[2]/button')
            continue
        # 선택 누르기(노선 고르기)
        click_by_xpath(driver, '/html/body/div[2]/div[2]/button')
        # 선택한 노선이 없습니다. 알람 확인
        alarm_accept(driver)
        # x버튼 누르기
        click_by_xpath(driver,'/html/body/div[2]/button')
    log('\n################################# Complete All Settings')

# 파일 list 읽기    
def read_filelist(path):
    try:
        #log('#### Read path {}'.format(path))
        file_list = list([])
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                try:
                    file_list.append(os.path.abspath(os.path.join(dirpath, f)))
                except:
                    log('######## Read file Error : {}'.format(filenames))
                    log('############ {}'.format(traceback.format_exc()))
        return file_list
    except:
        log('######################## Error : read_filelist')
        log('######## {}'.format(traceback.format_exc()))

# 다운로드 확인
def download_check(driver, path) :
    before_file_len = len(read_filelist(path))
    log(f'######## Before File Number : {before_file_len}')
    # 다운로드 버튼 누르기
    click_by_xpath(driver, '/html/body/div[1]/div[2]/form/div[3]/div[2]/div[2]/div[2]/div[2]/div[2]/div/h2/p/span/a')
    # [조회한 데이터 총 몇건] 확인 누르기 
    alarm_accept(driver)
    time_limit = 0
    while True:
        time_limit += 3
        time.sleep(3)
        after_file_len = len(read_filelist(path))
        log(f'######## After File Number : {after_file_len}')
        if before_file_len != after_file_len:
            time.sleep(5)
            break
        if time_limit > 200:
            log('################ File Donwload Failed')
            raise Exception('################ File Donwload Failed')
    log('################ File Donwload Success')

# 다운로드 파일 이름 변경    
def rename_file(path, rename_file_name):
    try :
        test = read_filelist(path)
        file_name = max(test, key=os.path.getmtime)
        os.rename(file_name, os.path.join(path, rename_file_name))
        log('################ File Rename Success')
    except :
        log('######################## Error : rename_file')
        log(traceback.format_exc())

# 년도 선택        
def select_year(driver, year):
    try :
        log('######## Select Year {}'.format(year))
        yearPicker = driver.find_element(by=By.XPATH, value='/html/body/div[7]/div/div/select[1]')
        options = yearPicker.find_elements(By.TAG_NAME, "option")
        for option in options:
            if option.get_attribute('innerHTML') == str(year):
                option.click()
                break
    except :
        log('######################## Error : select_year')
        log(traceback.format_exc())

# 달 선택        
def select_month(driver, month):
    try:
        log('######## Select Month {}'.format(month))
        monthPicker = driver.find_element(by=By.XPATH, value='/html/body/div[7]/div/div/select[2]')
        options = monthPicker.find_elements(By.TAG_NAME, "option")
        for option in options:
            if option.get_attribute('innerHTML') == str(month) +'월' :
                option.click()
                break
    except :
        log('######################## Error : select_month')
        log(traceback.format_exc())
# 일 선택        
def select_day(driver, day):
    try :
        log('######## Select Day {}'.format(day))
        datePicker = driver.find_element(by=By.XPATH, value='/html/body/div[7]')
        table = datePicker.find_element(By.TAG_NAME, "table")
        tbody = table.find_element(By.TAG_NAME, "tbody")
        trs = tbody.find_elements(By.TAG_NAME, 'tr')
        try:
            for tr in trs:
                try:
                    tds = tr.find_elements(By.TAG_NAME, 'td')
                    for td in tds:
                        try:
                            if td.get_attribute('innerHTML').split('>')[1].split('<')[0] == str(day):
                                td.click()
                                raise LoopBreak()
                        except :
                            pass
                except :
                    pass
        except LoopBreak:
            pass
    except :
        log('######################## Error : select_day')
        log(traceback.format_exc())
        
# 도시 선택        
def select_city(driver, place):
    try:
        log('#### Select City {}'.format(place))
        placePicker = driver.find_element(by=By.XPATH, value='/html/body/div[1]/div[2]/form/div[3]/div[2]/div[2]/div[1]/ul/li[2]/div/div[2]/ul[2]/li[2]/select')
        options = placePicker.find_elements(By.TAG_NAME, "option")
        for option in options :
            if option.get_attribute('innerHTML') == place:
                option.click()
                break
        log('######## Complete')
    except:
        log('######################## Error : select_city')
        log(traceback.format_exc())

# 경로 선택        
def search_route(driver, waytext, waytext2):
    try:
        popbox = driver.find_element(by=By.XPATH, value='/html/body/div[2]/div[1]/div[1]')
        table = popbox.find_element(By.TAG_NAME, "table")
        tbody = table.find_element(By.TAG_NAME, "tbody")
        trs = tbody.find_elements(By.TAG_NAME, 'tr')
        for tr in trs:
            tds = tr.find_elements(By.TAG_NAME, 'td')
            if tds[3].get_attribute('innerHTML').strip() == waytext and tds[1].get_attribute('innerHTML').strip() == waytext2:
                tds[0].click()
                return True
            else:
                continue
        return False
    except:
        log('######################## Error : search_route')
        log(traceback.format_exc())

# 길 선택        
def select_way(driver, waytext, waytext2):
    try:
        log('#### Select Way {} / {}'.format(waytext2, waytext))
        pop_box = driver.find_element(by=By.XPATH, value='/html/body/div[2]/div[1]/div[1]')
        pop_box_text = re.split(r'[<]', pop_box.get_attribute('innerHTML'))[0]
        find_format = re.compile('[0-9]+')
        total_waynum = int(find_format.search(pop_box_text).group())
        total_pagenumber = math.ceil(total_waynum / 10)
        log('######## Total Page Number : {}'.format(total_pagenumber))
        if total_pagenumber == 0:
            log('################ There is no matching Route')
            return False
        ## Pass Page
        present_pagenumber = 1
        for i in range(1, total_pagenumber + 1):
            if search_route(driver, waytext, waytext2) == True:
                log('######## Complete')
                return True
            else:
                log('############ Page {} No Route'.format(present_pagenumber))
            if present_pagenumber == total_pagenumber:
                log('################ There is no matching Route')
                return False
            if total_pagenumber > 10:
                if i % 10 == 0:
                    click_by_xpath(driver, '/html/body/div[2]/div[1]/div[2]/ul/li[{}]/a'.format(13))
                else:
                    click_by_xpath(driver, '/html/body/div[2]/div[1]/div[2]/ul/li[{}]/a'.format(i % 10 + 3))
            else:
                click_by_xpath(driver, '/html/body/div[2]/div[1]/div[2]/ul/li[{}]/a'.format(i + 1))
            present_pagenumber += 1
            log('############ Move to Page {}'.format(present_pagenumber))
            wait_loading(driver, '/html/body/div[5]/img')
    except:
        log('######################## Error : select_way')
        log(traceback.format_exc())

# 달력에 날짜 입력        
def select_calender_date(driver, calenderxpath, year, month, day):
    try:
        # 달력 클릭
        time.sleep(1)
        click_by_xpath(driver, calenderxpath)
        # 년도별 데이터 선택
        select_year(driver, year)
        # 월별 데이터 선택
        select_month(driver, month)
        # 일별 데이터 선택
        select_day(driver, day)
    except:
        log('######################## Error : select_calender_date')
        log(traceback.format_exc())

# 폴더 만들기         
def make_df(path):
    try:
        log('#### Make DataFrame')
        df_date = pd.read_csv(os.path.join(path, 'stcis_crawling_info_date.csv'))
        df_route = pd.read_csv(os.path.join(path, 'stcis_crawling_info_route.csv'))
        df_date['조회시작일'] = pd.to_datetime(df_date['조회시작일'])
        df_date['startyear'] = df_date['조회시작일'].dt.year
        df_date['startmonth'] = df_date['조회시작일'].dt.month
        df_date['startday'] = df_date['조회시작일'].dt.day
        log('######## Complete')
        return df_date , df_route
    except:
        log('######################## Error : make_df')
        log(traceback.format_exc())
        
# 대기        
def explicit_wait(driver, explicit_wait_xpath):
    try:
        WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, explicit_wait_xpath)))
    except:
        log('######################## Error : explicit_wait')
        log(traceback.format_exc())
        pass

# 클릭    
def click_by_xpath(driver, xpath):
    try:
        target = WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.XPATH, xpath)))  
        target.click()
        return target
    except:
        log('######################## Error : Click_by_xpath')
        log(traceback.format_exc())
        
if __name__=="__main__":
    main()
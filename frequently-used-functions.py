import logging
import os
import traceback
import re
import datetime
from logging.config import dictConfig
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By

# 로그 찍어주기
def log(msg):
    logging.info(msg)
    
class LoopBreak(Exception):
    pass
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

# 해당 컨텐츠가 안보일 때 까지 대기
def wait_loading(driver, xpath):
    try:
        WebDriverWait(driver, 1200).until(EC.invisibility_of_element((By.XPATH, xpath)))
    except:
        pass
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
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--window-size=1920x1080')
        # chrome_options.add_argument('--no-sandbox')
        # chrome_options.add_argument('--disable-dev-shm-usage')
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

# 파일 읽기
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

# 다운로드 한 파일 이름 변경
def rename_file(path, rename_file_name):
    try :
        test = read_filelist(path)
        file_name = max(test, key=os.path.getmtime)
        os.rename(file_name, os.path.join(path, rename_file_name))
        log('################ File Rename Success')
    except :
        log('######################## Error : rename_file')
        log(traceback.format_exc())

# 대기하기 
def explicit_wait(driver, explicit_wait_xpath):
    try:
        WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, explicit_wait_xpath)))
    except:
        log('######################## Error : explicit_wait')
        log(traceback.format_exc())
        pass
    
# 클릭하기
def click_by_xpath(driver, xpath):
    try:
        target = WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.XPATH, xpath)))  
        target.click()
        return target
    except:
        log('######################## Error : Click_by_xpath')
        log(traceback.format_exc())
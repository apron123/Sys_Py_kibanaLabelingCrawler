from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import csv
import pandas as pd
import re

# ziumks_kjh add 

# 웹드라이버 실행
driver_path = './chromedriver-win64/chromedriver.exe'

# 드라이버 옵션
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--ignore-certificate-errors')  # SSL/TLS 경고 무시

# chrome_options.add_argument('--headless')  # 백그라운드 모드로 실행

# Service 객체를 생성하여 ChromeDriver를 설정
service = Service(executable_path=driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# kibana URL
urls = pd.read_csv('./csv/urls.csv')
urlList = urls.url.to_list()

# 이미 라벨링한 한국어 필드리스트 삭제 함수 (필드리스트)
def remove_korean_elements(fieldList):
    filtered_list = []
    for field in fieldList:
        text = field.text
        if not re.search('[ㄱ-ㅎㅏ-ㅣ가-힣]+', text):
            filtered_list.append(field)
    return filtered_list
# 스크롤링 함수 (elm : 적용할 엘리먼트, n: 페이지다운 횟수)


def page_down_scroll(elm, n):
    elm.send_keys(Keys.PAGE_UP)
    time.sleep(0.3)
    for _ in range(n):
        elm.send_keys(Keys.END)


# 프로세스 실행
print("start")
print("--------------------------")
print("url count : ", len(urlList))
workCnt = 1

buttonText = ""
for url in urlList:
    time.sleep(2.0)
    
    print(f"work count : ({workCnt}/{len(urlList)})")
    driver.get(url)
    # 특정 요소가 로딩될 때까지 대기
    wait = WebDriverWait(driver, 30)  # 최대 30초 동안 대기
    
    element = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, '.euiAccordion__childWrapper')))
    data = pd.read_csv('./csv/standard_code.csv')
    data.cd = data.cd.str.lower()
    nm = data.nm
    cd = data.cd
        
    time.sleep(0.5)
    try:
        toastCloseButton = WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test-subj="toastCloseButton"]')))
    
        toastCloseButton.click()
        time.sleep(0.5)
    except:
        print("kibana popup pass")
        pass
             
    filterType = driver.find_element(
        By.CSS_SELECTOR, '[data-test-subj="toggleFieldFilterButton"]')
    filterType.click()
    
    time.sleep(0.5)    
        
    try:
        filterToggle = driver.find_element(
            By.CSS_SELECTOR, '[data-test-subj="missingSwitch"][aria-checked="true"]')
        filterToggle.click()
        time.sleep(0.5)
    except:
        pass
    filterType.click()
    time.sleep(0.5)

    scroll = driver.find_element(
        By.CSS_SELECTOR, '.euiAccordion__childWrapper')
    page_down_scroll(scroll, 30)
    time.sleep(1.0)

    fieldList = driver.find_elements(By.CSS_SELECTOR, '.dscSidebarField__name')
    filter_df = pd.DataFrame({
        'f_nm': [element.text for element in fieldList]
    })
    result_df = data[data['cd'].isin(filter_df['f_nm'])]

    fieldCdList = result_df.cd.tolist()
    print(" - field count : ", len(fieldCdList))
    
        
    time.sleep(0.5)
    #실제 필드 표준화한 개수 0개 이상일 경우 Save discover 해야함.
    fieldCount = 0
    
    for cd in fieldCdList:
        scroll = driver.find_element(
            By.CSS_SELECTOR, '.euiAccordion__childWrapper')
        page_down_scroll(scroll, 30)
        time.sleep(1.0)

        fieldList = driver.find_elements(
            By.CSS_SELECTOR, '.dscSidebarField__name')
       
        time.sleep(2.0)
        fieldList = remove_korean_elements(fieldList)
        fieldNm = result_df[result_df.isin([cd]).any(axis=1)].nm.tolist()

        if len(fieldNm) > 0:
            for field in fieldList:
                try:
                    if cd == field.text:
                        field.click()
                        time.sleep(0.5)
                        label_edit = driver.find_element(
                            By.CSS_SELECTOR, '[data-test-subj="discoverFieldListPanelEditItem"]')
                        label_edit.click()
                        time.sleep(0.5)
                        try:
                            # "aria-label" 속성이 "Set custom label"이고 "aria-checked" 속성이 "false"인 요소 가져오기
                            toggle = driver.find_element(
                                By.CSS_SELECTOR, '[aria-label="Set custom label"][aria-checked="false"]')
                            toggle.click()
                            time.sleep(0.5)
                            input = driver.find_element(
                                By.CSS_SELECTOR, '[data-test-subj="customLabelRow"] [data-test-subj="input"]')
                            input.send_keys(fieldNm[0])
                            time.sleep(0.5)
                            
                            
                            save = driver.find_element(
                                By.CSS_SELECTOR, '[data-test-subj="fieldSaveButton"]')
                            save.click()
                            time.sleep(1.0)
                            
                            # 키바나 표준화 끝난 필드를 Available fields 로 옮김. - > 버튼 클릭하여
                            # fieldToggleButton = driver.find_element(
                            # By.CSS_SELECTOR, '[data-test-subj="fieldToggle-'+cd+ '"]')
                            
                            
                            fieldToggleButton = driver.find_element(
                            By.CSS_SELECTOR, '[data-test-subj="fieldToggle-'+field.text+'"]')
                            
                            fieldToggleButton.click()
                            time.sleep(1.0)
                            
                            fieldCount = fieldCount+1
                        except:
                            print(" -", field.text, "error")
                            # print(" -", cd, "error")
                            close = driver.find_element(
                                By.CSS_SELECTOR, '[data-test-subj="closeFlyoutButton"]')
                            close.click()
                            time.sleep(1.0)
                except:
                    print(" -", field.text, "error")
                    # print(" -", cd, "error")
                    field.click()
                    time.sleep(0.5)
                    pass
                
    if fieldCount > 0:
        
            # Save 버튼 클릭
            save_button = driver.find_element(By.CSS_SELECTOR, '[data-test-subj="discoverSaveButton"]')
            save_button.click()
            time.sleep(2.0)
                                    
            # 버튼의 텍스트 가져오기
            button_text = driver.find_element(By.CSS_SELECTOR, '.euiButton__text strong').text
            print('SUCCESS Discover'+button_text)
            savedObjectTitle = driver.find_element(
                                        By.CSS_SELECTOR, '[data-test-subj="savedObjectTitle"]')
            savedObjectTitle.send_keys(button_text)

            confirmSaveSavedObjectButton = driver.find_element(
                                        By.CSS_SELECTOR, '[data-test-subj="confirmSaveSavedObjectButton"]')
            confirmSaveSavedObjectButton.click()
            time.sleep(1.0)
            buttonText = button_text
            time.sleep(1.0)
    workCnt += 1
# 프로세스 종료
print("--------------------------")
print("stop...")
print(buttonText)
driver.quit()

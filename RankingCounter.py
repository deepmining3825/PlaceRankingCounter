import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from time import sleep
from bs4 import BeautifulSoup
import re
import json

# place리스트 to 튜플 리스트
with open ("Place.json", "r", encoding="UTF-8") as p:
    placeData = json.load(p)
if len(placeData) > 0:
    placeList = []
    for idx in range(len(placeData)):
        dict = placeData[idx]
        placeList.append(dict)


# --크롬창을 숨기고 실행-- driver에 options를 추가해주면된다
option = Options()
#option.add_argument('headless')

# css 찾을때 까지 10초대기
def time_wait(num, code):
    try:
        wait = WebDriverWait(driver, num).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, code)))
    except:
        print(code, '태그를 찾지 못하였습니다.')
        driver.quit()
    return wait

# frame 변경 메소드
def switch_frame(frame):
    driver.switch_to.default_content()  # frame 초기화
    driver.switch_to.frame(frame)  # frame 변경
    #res
    #soup


# 페이지 다운
def page_down(num):
    body = driver.find_element(By.CSS_SELECTOR,'body')
    body.click()
    for i in range(num):
        body.send_keys(Keys.PAGE_DOWN)

    
def getStoreList():
    store_list1 = driver.find_elements(By.CLASS_NAME,'qbGlu > div:first-child + div.ouxiq > a.P7gyV > div.ApCpt > div.C6RjW > span.YwYLL') #플레이스
    store_list2 = driver.find_elements(By.CLASS_NAME,'UEzoS > div.CHC5F:first-child > a.tzwk0 > div.bSoi3 > div.N_KDL > span.TYaxT') #레스토랑
    store_list3 = driver.find_elements(By.CLASS_NAME,'p0FrU > div.QTjRp:first-child > a.JpTbw > div.G9H9r > div.tWIhh > span.O_Uah') #미용실
    store_list4 = driver.find_elements(By.CLASS_NAME,'DWs4Q > div:first-child + div.IPtqD > a.gqFka > div.LYTmB > div.yxaf3 > span.q2LdB') #병원
    store_list5 = driver.find_elements(By.CLASS_NAME,'p0FrU > div.QTjRp:first-child > a.JpTbw > div.G9H9r > div.tWIhh > span.O_Uah') #네일샵

    if len(store_list1) > 0:
        return store_list1
    elif len(store_list2) > 0:
        return store_list2
    elif len(store_list3) > 0:
        return store_list3
    elif len(store_list4) > 0:
        return store_list4
    else:
        return store_list5

datas = []
driver = webdriver.Chrome('/chromedriver', options=option)  # 드라이버 경로
for place in placeList:
    url = 'https://map.naver.com/v5/search'
    driver.get(url)
    key_word = place.get('Keyword') # 검색어

    # css를 찾을때 까지 10초 대기
    time_wait(10, 'div.input_box > input.input_search')

    # 검색창 찾기
    search = driver.find_element(By.CSS_SELECTOR,'div.input_box > input.input_search')
    search.send_keys(key_word)  # 검색어 입력
    search.send_keys(Keys.ENTER)  # 엔터버튼 누르기

    res = driver.page_source  # 페이지 소스 가져오기
    soup = BeautifulSoup(res, 'html.parser')  # html 파싱하여  가져온다

    sleep(1)

    # frame 변경
    switch_frame('searchIframe')
    page_down(40)
    sleep(5)

    # 페이지 리스트
    next_btn = driver.find_elements(By.CLASS_NAME,'zRM9F > a')
    ad_stores = []
    stores = []
    find = False
    for btn in range(len(next_btn))[1:]:
        result = ""
        next_btn[btn].click()
        sleep(2)
        store_list = getStoreList()

        for store in store_list:
            stores.append(store.text)
    print("==================제거전====================")
    print(stores)
    print("===========================================")

    for i in range(len(stores)):
        if stores[i] == place.get('Name'):
            result = str(i+1) + "위"
            break
        else:
            result = "순위에 없음"

    data = {'키워드': place.get('Keyword'), '업체명': place.get('Name'), '순위': result}
    datas.append(data)

    
driver.quit()  # 작업이 끝나면 창을닫는다.
f = open("Ranking.txt",'w', encoding="UTF-8")
for data in datas:
    f.write(str(data)+"\n")
f.close()
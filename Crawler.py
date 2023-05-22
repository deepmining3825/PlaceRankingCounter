from selenium.webdriver.common.by import By
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import re
from selenium.webdriver.common.keys import Keys
import time
import requests
import openpyxl
import json
import io
import sys

buffer = io.StringIO()
sys.stdout = buffer
sys.stderr = buffer

# 스크롤 횟수 설정
f = open("scroll.txt", "r")
line = f.readline()
f.close()

# place리스트 to 튜플 리스트
with open ("Keyword.json", "r", encoding="UTF-8") as p:
    placeData = json.load(p)
if len(placeData) > 0:
    placeList = []
    for idx in range(len(placeData)):
        dict = placeData[idx]
        placeList.append(dict)

for place in placeList:
    #크롬 웹드라이버 불러오기
    driver = webdriver.Chrome(ChromeDriverManager().install())
    res = driver.get('https://m.place.naver.com/place/list?query=' + place.get('Keyword') + '&level=top')
    driver.implicitly_wait(20)

    #2차 크롤링을 위한 bs4 셋팅
    session = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G885S) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.58 Mobile Safari/537.36"}

    retries = Retry(total=5,
                    backoff_factor=0.1,
                    status_forcelist=[ 500, 502, 503, 504 ])

    session.mount('http://', HTTPAdapter(max_retries=retries))

    #body부분을 잡기 위해 쓸데없이 버튼을 클릭해줌
    driver.find_element(By.XPATH, '//*[@id="_list_scroll_container"]/div/div/div[1]/div/div/a[2]').click()
    driver.find_element(By.XPATH, '//*[@id="_list_scroll_container"]/div/div/div[1]/div/div/a[1]').click()

    #검색결과가 모두 보이지 않기 때문에 page down을 눌러 끝까지 펼쳐준다.
    for scroll in range(0,int(line)):
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
        time.sleep(0.2)

    html = driver.page_source
    bs = BeautifulSoup(html, 'html.parser')
    soup = bs.select_one('div.YluNG')
    naver_info = soup.select('li.VLTHu:not(.hTu5x)')

    # 새로운 워크북 만들기
    wb = openpyxl.Workbook()
    # 현재 시트 선택
    sheet = wb.active
    # 헤더 추가하기
    sheet.append(["업체명", "전화번호", "주소", "플레이스", "웹사이트1", "웹사이트2"])

    #2차 크롤링을 위한 url
    url = 'https://m.place.naver.com'
    
    for info in naver_info:
        store_name = info.select_one('span.YwYLL').text
        link = info.select_one('div.ouxiq').select_one('a').attrs['href']
        # link = info.select_one('qbGlu > div:not(a ~ div) > a.P7gyV').attrs['href']
        time.sleep(0.06)

        # #네이버 플레이스로 이동(place ID로 접속)
        webAddress = url+link
        N_res = session.get(webAddress, headers=headers)
        
        N_soup_srch = BeautifulSoup(N_res.content, 'html.parser')
        try:
            oldtel = N_soup_srch.select_one('span.yxkiA > a').attrs['href']
            tel = str(re.sub('tel:', '', oldtel))
        except:
            tel = '#'
        try:
            website1 = N_soup_srch.select_one('div.jO09N > a').attrs['href']
        except:
            website1 = '#'
        try:
            website2 = N_soup_srch.select_one('div.Cycl8 > span.S8peq > a').attrs['href']
        except:
            website2 = '#'
        try:
            address = N_soup_srch.select('span.yxkiA > a')[3].attrs['data-line-description']
        except:
            address = '#'
        sheet.append([store_name, tel, address, webAddress, website1, website2])
        time.sleep(0.06)
    wb.save(place.get('Keyword') + " 플레이스 크롤링 결과.xlsx")

driver.quit()
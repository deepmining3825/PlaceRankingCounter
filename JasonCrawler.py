from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import pymysql
from time import sleep

def getDriver():
    option = Options()
    driver = webdriver.Chrome('/chromedriver', options=option)  # 드라이버 경로
    return driver

# jasonDB에 접속 후 발행매체, 키워드 쌍을 획득
def getKeywordList(target):
    conn = pymysql.connect(host='34.172.204.75', user='cmcm', password='cm1234', db='jasondb', charset='utf8')
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT publisher, " + target[0] + " FROM board ORDER BY publisher ASC")
    rawData = [item for item in cur.fetchall()]
    keywordList = [(item[0], item[1]) for item in rawData]
    conn.close()
    return keywordList

# jasonDB에 접속 후 데이터의 ID, URL을 획득
def getDataList(publisher, keyword, target):
    conn = pymysql.connect(host='34.172.204.75', user='cmcm', password='cm1234', db='jasondb', charset='utf8')
    cur = conn.cursor()
    cur.execute("SELECT id, url FROM board WHERE publisher = '" + publisher + "' and " + target[0] + " = '" + keyword + "'")
    rawData = [item for item in cur.fetchall()]
    dataList = [(item[0], item[1]) for item in rawData]
    conn.close()
    return dataList

def press(driver, keyword, target):
    dataList = getDataList('언론보도', keyword, target)
    driver.get('https://search.naver.com/search.naver?where=news&sm=tab_jum&query=' + keyword)
    driver.implicitly_wait(20)

    session = requests.Session()
    retries = Retry(total=5,
                    backoff_factor=0.1,
                    status_forcelist=[ 500, 502, 503, 504 ])

    session.mount('http://', HTTPAdapter(max_retries=retries))

    next_btn = driver.find_elements(By.CLASS_NAME,'sc_page_inner > a')
    links = []
    for btn in next_btn:
        link = btn.get_attribute("href")
        links.append(link)

    urlList = []

    for link in links:
        driver.get(link)
        sleep(1)
        html = driver.page_source
        bs = BeautifulSoup(html, 'html.parser')
        soup = bs.find_all("li", {"class": "bx"})

        for i in soup:
            m = i.select_one("[data-url]")
            try:
                url = m["data-url"]
                urlList.append(url)
            except:
                pass
        
    for item in dataList:
        rank = 0
        for idx in range(0, len(urlList)):
            if item[1] == urlList[idx]:
                rank = idx+1
                update(str(rank), item[0], target)
                #print("id:" + str(item[0]) + ", rank:" + str(rank))
        if rank == 0:
            update("순위 밖", item[0], target)
            #print("id:" + str(item[0]) + ", rank: 순위 밖")

def kin(driver, keyword, target):
    dataList = getDataList('지식인', keyword, target)
    driver.get('https://search.naver.com/search.naver?where=kin&sm=tab_jum&query=' + keyword)
    driver.implicitly_wait(20)

    session = requests.Session()
    retries = Retry(total=5,
                    backoff_factor=0.1,
                    status_forcelist=[ 500, 502, 503, 504 ])

    session.mount('http://', HTTPAdapter(max_retries=retries))

    next_btn = driver.find_elements(By.CLASS_NAME,'sc_page_inner > a')
    links = []
    for btn in next_btn:
        link = btn.get_attribute("href")
        links.append(link)

    urlList = []
    
    for link in links:
        driver.get(link)
        sleep(1)
        html = driver.page_source
        bs = BeautifulSoup(html, 'html.parser')
        soup = bs.find_all("li", {"class": "bx _svp_item"})
        
        for i in soup:
            m = i.select_one("[data-url]")
            try:
                url = m["data-url"]
                urlList.append(url)
            except:
                pass

    for item in dataList:
        url_start = item[1].split('naver?')
        url1 = url_start[0] + 'naver?'
        url_end = item[1].split('dirId')
        url2 = 'dirId' + url_end[1]
        url = url1 + url2
        rank = 0
        for idx in range(0, len(urlList)):
            if url == urlList[idx]:
                rank = idx+1
                update(str(rank), item[0], target)
#                print("id:" + str(item[0]) + ", rank:" + str(rank))
        if rank == 0:
            update("순위 밖", item[0], target)
    #        print("id:" + str(item[0]) + ", rank: 순위 밖")

def viewTab(driver, keyword, target):
    dataList = getDataList('뷰탭', keyword, target)
    driver.get('https://search.naver.com/search.naver?where=view&sm=tab_viw.blog&query=' + keyword)
    driver.implicitly_wait(20)

    session = requests.Session()
    retries = Retry(total=5,
                    backoff_factor=0.1,
                    status_forcelist=[ 500, 502, 503, 504 ])

    session.mount('http://', HTTPAdapter(max_retries=retries))

    driver.find_element(By.CSS_SELECTOR, 'div.greenbox').click()

    for scroll in range(0,50):
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
        time.sleep(0.2)

    html = driver.page_source
    bs = BeautifulSoup(html, 'html.parser')
    soup = bs.find_all("li", {"class": "bx _svp_item"})
    urlList = []
    for i in soup:
        m = i.select_one("[data-url]")
        try:
            url = m["data-url"]
            urlList.append(url)
        except:
            pass

    for item in dataList:
        rank = 0
        for idx in range(0, len(urlList)):
            if item[1] == urlList[idx]:
                rank = idx+1
                update(str(rank), item[0], target)
        if rank == 0:
            update("순위 밖", item[0], target)

def update(rank, id, target):
    conn = pymysql.connect(host='34.172.204.75', user='cmcm', password='cm1234', db='jasondb', charset='utf8')
    cur = conn.cursor()
    sql = "UPDATE board SET " + target[1] + " = %s WHERE id = %s"
    cur.execute(sql, (rank, id))
    conn.commit()
    conn.close()

def main():
    driver = getDriver()
    targetList = [('keyword1', 'ranking1'), ('keyword2', 'ranking2'), ('keyword3', 'ranking3'), ('keyword4', 'ranking4'), ('keyword5', 'ranking5'), ('keyword6', 'ranking6'), ('keyword7', 'ranking7'), ('keyword8', 'ranking8'), ('keyword9', 'ranking9'), ('keyword10', 'ranking10')]
    for target in targetList:
        keywordList = getKeywordList(target)
        for item in keywordList:
            if item[0] == '뷰탭':
                if item[1] != '':
                    viewTab(driver, item[1], target)
            elif item[0] == '언론보도':
                if item[1] != '':
                    press(driver, item[1], target)
            elif item[0] == '지식인':
                if item[1] != '':
                    kin(driver, item[1], target)
    
if __name__ == '__main__':
    main()
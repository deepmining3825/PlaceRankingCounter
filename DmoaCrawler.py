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

# dmoaDB에 접속 후 발행매체, 키워드 쌍을 획득
def getKeywordList():
    conn = pymysql.connect(host='183.111.141.82', user='sbfrog_dmoa', password='dmoa00!!', db='sbfrog_dmoa', charset='utf8')
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT wr_4, wr_6 FROM g5_write_free ORDER BY wr_4 ASC")
    rawData = [item for item in cur.fetchall()]
    keywordList = [(item[0].decode('utf-8'), item[1].decode('utf-8')) for item in rawData]
    conn.close()
    return keywordList

# dmoaDB에 접속 후 데이터의 ID, URL을 획득
def getDataList(publisher, keyword):
    conn = pymysql.connect(host='183.111.141.82', user='sbfrog_dmoa', password='dmoa00!!', db='sbfrog_dmoa', charset='utf8')
    cur = conn.cursor()
    cur.execute("SELECT wr_id, wr_link1 FROM g5_write_free WHERE wr_4 = '" + publisher + "' and wr_6 = '" + keyword + "'")
    rawData = [item for item in cur.fetchall()]
    dataList = [(item[0], item[1].decode('utf-8')) for item in rawData]
    conn.close()
    return dataList

def viewTab(keyword):
    dataList = getDataList('뷰탭', keyword)

    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get('https://search.naver.com/search.naver?where=view&sm=tab_viw.blog&query=' + keyword)
    driver.implicitly_wait(20)

    session = requests.Session()
    retries = Retry(total=5,
                    backoff_factor=0.1,
                    status_forcelist=[ 500, 502, 503, 504 ])

    session.mount('http://', HTTPAdapter(max_retries=retries))

    driver.find_element(By.CSS_SELECTOR, 'div.greenbox').click()

    for scroll in range(0,30):
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
                update(str(rank), item[0])
#                print("id:" + str(item[0]) + ", rank:" + str(rank))
        if rank == 0:
            pass
            update("밖", item[0])
#            print("id:" + str(item[0]) + ", rank:밖")

def press(keyword):
    print(keyword)

def kin(keyword):
    print(keyword)


def update(rank, id):
    conn = pymysql.connect(host='183.111.141.82', user='sbfrog_dmoa', password='dmoa00!!', db='sbfrog_dmoa', charset='utf8')
    cur = conn.cursor()
    sql = "UPDATE g5_write_free SET wr_2 = %s WHERE wr_id = %s"
    cur.execute(sql, (rank, id))
    conn.commit()
    conn.close()

def main():
    keywordList = getKeywordList()
    for item in keywordList:
        if item[0] == '뷰탭':
            viewTab(item[1])
    #     elif item[0] == '언론보도':
    #         press(item[1])
    #     elif item[0] == '지식인':
    #         kin(item[1])    
    
if __name__ == '__main__':
    main()
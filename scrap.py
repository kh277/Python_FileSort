from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sqlite3


# 전역 변수
subClass = ['Acoustic', 'Afro House', 'Ambient', 'Bass', 'Bass House',
            'Breaks', 'Chillout', 'Dance', 'Dance / Electro Pop', 'Deep House',
            'DJ Tools', 'Downtempo', 'Drift Phonk', 'Drum & Bass', 'Drumstep',
            'Dubstep', 'Electro', 'Electro House', 'Electronic', 'Electronica',
            'Future Bass', 'Future Rave', 'Garage', 'Glitch Hop', 'Halftime',
            'Happy Hardcore', 'Hard Dance', 'House', 'Indie Dance', 'Indie Dance / Nu Disco',
            'Melodic Bass', 'Melodic House & Techno', 'Midtempo', 'Moombahcore', 'Moombahton',
            'Nu Disco', 'Nu Disco / Disco', 'Orchestral', 'Organic House', 'Organic House / Downtempo',
            'Pop', 'Progressive House', 'Psy-Trance', 'Rock', 'Speed House',
            'Synthwave', 'Tech House', 'Techno', 'Trance', 'Trance (Raw / Deep / Hypnotic)',
            'Trap', 'Trap / Hip-Hop / R&B', 'UK Garage / Bassline']

month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

catalogURL = "https://player.monstercat.app/catalog?s=&any=catalog&offset="
releaseURL = "https://player.monstercat.app/releases?limit=0&sort=&offset="
CATALOG_PAGE_COUNT = 100
RELEASE_PAGE_COUNT = 24


# KMP 실패 함수
def getFail(pattern):
    fail = [0 for _ in range(len(pattern))]

    j = 0
    for i in range(1, len(pattern)):
        while j > 0 and pattern[i] != pattern[j]:
            j = fail[j-1]

        if pattern[i] == pattern[j]:
            j += 1
            fail[i] = j

    return fail


# KMP 함수
def KMP(text, pattern):
    fail = getFail(pattern)

    result = []
    j = 0
    for i in range(len(text)):
        while j > 0 and text[i] != pattern[j]:
            j = fail[j-1]

        if text[i] == pattern[j]:
            if j == len(pattern)-1:
                result.append(i-len(pattern)+2)
                j = fail[j]
            else:
                j += 1
    
    return result


# catalog 페이지 스크래핑
def scrapCatalog():
    # 데이터베이스 초기 설정
    conn = sqlite3.connect('musicData.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY,
            fileName TEXT,
            brand TEXT,
            genre TEXT)
    ''')
    conn.commit()

    # 브라우저 꺼짐 방지 옵션
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)

    # webdriver 객체 생성 및 설정
    driver = webdriver.Chrome(options=chrome_options)       # webdriver 객체 설정
    driver.set_window_size(1280,720)        # 창 크기 HD로 설정

    # url로 접속
    url = catalogURL + '0'
    driver.get(url)
    wait = WebDriverWait(driver, 10)  # 최대 10초 대기
    curPageData = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#wrapper > div.content-container > div:nth-child(4) > div > nav > span')))
    parseCurPage = list(curPageData.text.split())

    # 모든 페이지에 대해 처리
    for i in range(0, int(parseCurPage[4]), CATALOG_PAGE_COUNT):
        # 해당하는 인덱스 url로 이동
        url = catalogURL + str(i)
        driver.get(url)

        # 웹 페이지의 tbody 태그가 로드되면 데이터를 받아오기
        htmlData = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#wrapper > div.content-container > div:nth-child(4) > div > table > tbody')))
        parseHtml = htmlData.text.split("\n")

        # 받아온 데이터를 전처리 후 파일명, 브랜드, 장르를 각각 DB에 저장
        for index in range(0, len(parseHtml), 4):
            fileName = parseHtml[index+2] + " - " + parseHtml[index] + ".mp3"
            brand = parseHtml[index+3].split()[-1]
            etc = parseHtml[index+3]
            genre = None

            for curMonth in month:
                temp = KMP(etc, curMonth)
                if len(temp) != 0:
                    genre = etc[:temp[0]-2]

            cursor.execute('INSERT INTO songs (fileName, brand, genre) VALUES (?, ?, ?)', (fileName, brand, genre))
            conn.commit()

    driver.quit()
    conn.close()

    print("노래 추출 완료", flush=True)
    return True


# release 페이지 스크래핑
def scrapRelease():
    # 데이터베이스 초기 설정
    conn = sqlite3.connect('musicData.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY,
            fileName TEXT,
            brand TEXT,
            genre TEXT)
    ''')
    conn.commit()

    # 브라우저 꺼짐 방지 옵션
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)

    # webdriver 객체 생성 및 설정
    driver = webdriver.Chrome(options=chrome_options)       # webdriver 객체 설정
    driver.set_window_size(1280,720)        # 창 크기 HD로 설정

    # url로 접속
    url = releaseURL + '0'
    driver.get(url)
    wait = WebDriverWait(driver, 10)  # 최대 10초 대기
    curPageData = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#wrapper > div.content-container > nav > span')))
    parseCurPage = list(curPageData.text.split())

    # 모든 페이지에 대해 처리
    for i in range(0, int(parseCurPage[4]), RELEASE_PAGE_COUNT):
        # 해당하는 인덱스 url로 이동
        url = releaseURL + str(i)
        driver.get(url)

        # 웹 페이지의 tbody 태그가 로드되면 데이터를 받아오기
        htmlData = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#wrapper > div.content-container > div.row.release-list.mr-2.ml-2')))
        parseHtml = htmlData.text.split("\n")

        # 받아온 데이터를 전처리 후 파일명, 브랜드, 장르를 각각 DB에 저장
        for index in range(0, len(parseHtml), 4):
            fileName = parseHtml[index+2] + " - " + parseHtml[index] + ".mp3"
            brand = parseHtml[index+3].split()[-1]
            etc = parseHtml[index+3]
            genre = None

            for curMonth in month:
                temp = KMP(etc, curMonth)
                if len(temp) != 0:
                    genre = etc[:temp[0]-2]

            cursor.execute('INSERT INTO songs (fileName, brand, genre) VALUES (?, ?, ?)', (fileName, brand, genre))
            conn.commit()

    driver.quit()
    conn.close()

    print("노래 추출 완료", flush=True)
    return True


def main():
    try:
        return scrapCatalog()
    except:
        return False
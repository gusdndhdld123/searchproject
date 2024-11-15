from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from flask import Flask, render_template, jsonify
import pyperclip
import time
import threading
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import json
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from flask_cors import CORS
import datetime
import math

app = Flask(__name__)
CORS(app, origins="*")

# 로그 레벨 설정
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler = logging.StreamHandler()
log_handler.setFormatter(log_formatter)
app.logger.addHandler(log_handler)
app.logger.setLevel(logging.INFO)
logging.getLogger().addHandler(log_handler)
logging.getLogger().setLevel(logging.INFO)

# 전역 변수를 통해 드라이버 상태 유지
driver = None
count1 = 0
maxcount = 3600 * 24  # 30초로 변경 (테스트 목적, 실제 3600초로 설정 가능)

def initialize_driver():
    """WebDriver 초기화 및 전역 변수 설정."""
    global driver
    if driver is None:  # 이미 드라이버가 초기화되었으면 재사용
        options = Options()
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        driver.set_window_size(1920, 1080)
        app.logger.info('WebDriver 초기화 완료')

def counthour():
    """1초마다 count1을 1씩 증가시키고, 3600초 후 naver_login 함수 호출"""
    global count1
    if count1 < maxcount:
        count1 += 1
        app.logger.info(f"현재 count1: {count1} / 목표 maxcount: {maxcount}")
    else:
        app.logger.info(f"{maxcount}초가 경과하였습니다. 네이버 로그인 시작.")
        naver_login()  # 3600초 후 로그인 함수 호출
        count1 = 0  # 카운트를 초기화하여 다시 카운트할 수 있게 설정

def naver_login():
    """네이버와 스토어에 로그인."""
    if driver is None:
        initialize_driver()  # 드라이버가 초기화되지 않았다면 초기화

    # 항상 새 창을 열어 네이버 페이지 접속
    driver.execute_script("window.open('');")
    # driver.switch_to.window(driver.window_handles[-1])  # 새 창으로 전환
    # driver.get("https://www.naver.com/")
    # app.logger.info('새 창에 네이버 페이지 열림')
    # time.sleep(2)
    #
    # # 로그아웃 처리 (로그인 상태일 경우)
    # try:
    #     logout_button = driver.find_element(By.CLASS_NAME, "MyView-module__btn_logout___bsTOJ")
    #     logout_button.click()
    #     app.logger.info("로그아웃 버튼 클릭됨")
    # except Exception as e:
    #     app.logger.info(f"로그아웃 버튼이 존재하지 않음: {e}")
    #
    # # 로그인 버튼 클릭 및 로그인 정보 입력
    # login_button1 = driver.find_element(By.CLASS_NAME, "MyView-module__link_login___HpHMW")
    # login_button1.click()
    # time.sleep(2)
    # app.logger.info('로그인 버튼 클릭')
    #
    # #로그인 유지 버튼 누름
    # keepbutton1 = driver.find_element(By.CLASS_NAME, "keep_text")
    # keepbutton1.click()
    #
    #
    # # 아이디와 패스워드 입력
    # id_input = driver.find_element(By.ID, "id")
    # id_input.click()
    # pyperclip.copy("althcjswo11")
    # actions = ActionChains(driver)
    # actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
    # time.sleep(3)
    # app.logger.info('아이디 입력됨')
    #
    # pw_input = driver.find_element(By.ID, "pw")
    # pw_input.click()
    # pyperclip.copy("alth9524!!")
    # actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
    # app.logger.info('패스워드 입력됨')
    # time.sleep(3)
    # pw_input.send_keys(Keys.ENTER)
    # app.logger.info('엔터 입력됨')
    # time.sleep(3)  # 로그인 대기
    #
    # # 스토어 페이지로 이동하여 간편 로그인
    # driver.execute_script("window.open('https://accounts.commerce.naver.com/login?url=https%3A%2F%2Fsell.smartstore.naver.com%2F%23%2Flogin-callback');")
    # driver.switch_to.window(driver.window_handles[-1])
    # app.logger.info('스토어 페이지 새 창 열림')
    # time.sleep(4)
    #
    # login_button2 = driver.find_element(By.CLASS_NAME, "Login_btn_login__2TtMz")
    # login_button2.click()
    # app.logger.info('스토어 간편로그인 버튼 클릭')
    #
    # # 추가 처리
    # try:
    #     button0 = driver.find_element(By.CLASS_NAME, "LinkSmartStore_lnk__21yae")
    #     button0.click()
    #     app.logger.info("추가처리 버튼 클릭됨")
    # except Exception as e:
    #     app.logger.info(f"추가처리 버튼이 존재하지 않음: {e}")
    #
    # # 기존 다른 모든 창 닫기 (로그인 완료 후)
    # if len(driver.window_handles) > 2:  # 기존 창이 있는 경우에만 실행
    #     for handle in driver.window_handles[:-1]:
    #         driver.switch_to.window(handle)
    #         driver.close()
    #     app.logger.info('기존 모든 창 닫음')
    #
    # # 마지막 남은 창으로 전환
    # driver.switch_to.window(driver.window_handles[0])


def get_search_data(keyword):
    """키워드를 이용해 검색 데이터를 가져옴."""
    if driver is None:
        initialize_driver()  # 드라이버가 초기화되지 않았다면 초기화
    if len(driver.window_handles) < 3:
        driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[2])
    driver.get(f"https://sell.smartstore.naver.com/api/product/shared/product-search-popular?_action=productSearchPopularByKeyword&keyword={keyword}")

    app.logger.info('검색창 열림')
    page_source = driver.page_source
    start_index = page_source.find("{")
    end_index = page_source.rfind("}")
    json_data = page_source[start_index:end_index + 1]
    data = json.loads(json_data)
    app.logger.info('데이터 추출 완료')
    return data

def scheduled_task():
    """주기적으로 실행할 작업."""
    counthour()  # 주기적으로 카운트 작업을 실행

def on_startup():
    """서버 시작 시 한 번만 실행할 작업."""
    naver_login()  # 서버 시작 시 한 번만 실행
# schedule.start()
def initialize_app():
    """서버 시작 시 필요한 초기화 작업."""
    global driver
    if driver is None:
        initialize_driver()  # 드라이버 초기화

    # Smartstore URL에 접속한 상태가 아니면 로그인 시도
    if not driver.current_url.startswith("https://sell.smartstore.naver.com"):
        naver_login()  # 네이버 로그인
# 스케줄러 작업
schedule = BackgroundScheduler(daemon=True, timezone='Asia/Seoul')

# # 1초 간격으로 실행되는 카운트 작업
# schedule.add_job(counthour, 'interval', seconds=1, id='test_job', max_instances=1)
# 서버 시작 시 단 한 번 실행되는 작업 추가
schedule.add_job(initialize_app, trigger=DateTrigger(run_date=datetime.datetime.now()))

# # 서버 시작 시 한 번만 실행되는 로그인 작업 (즉시 실행)
# schedule.add_job(on_startup, 'interval', seconds=0, id='login_job', max_instances=1)
#
# # 스케줄러 시작

@app.route('/login', methods=['GET'])
def index():
    global driver

    if driver is None:
        initialize_driver()  # 드라이버 초기화

    if not driver.current_url.startswith("https://sell.smartstore.naver.com"):
        naver_login()  # 네이버 로그인

    return render_template('index.html', data=None)

@app.route('/api/<keyword>', methods=['GET'])
def api(keyword):
    global driver
    if driver is None:
        initialize_driver()  # 드라이버 초기화

    # API 요청에 대해 별도 쓰레드로 처리
    thread = threading.Thread(target=get_search_data, args=(keyword,))
    thread.start()
    thread.join()  # 필요시 join() 사용해 대기
    data = get_search_data(keyword)

    return jsonify(data)

# def scheduled_task():
#     """주기적으로 실행할 작업."""
#     counthour()  # 주기적으로 카운트 작업을 실행

if __name__ == '__main__':
    # # APScheduler 설정
    # scheduler = BackgroundScheduler(daemon=True, timezone='Asia/Seoul')
    # scheduler.add_job(scheduled_task, 'interval', seconds=1)
    #
    # # 서버 시작 시 스케줄러 시작
    # scheduler.start()
    initialize_app()  # 서버 시작 시 한 번 초기화 함수 실행
    # Flask 서버 실행, use_reloader=False로 설정하여 두 번 실행되지 않도록 방지
    app.run(debug=False, use_reloader=False)

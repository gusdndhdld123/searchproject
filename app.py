from apscheduler.schedulers.background import BackgroundScheduler
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

# 전역 변수를 통해 드라이버 상태 유지
driver = None

def initialize_driver():
    """WebDriver 초기화 및 전역 변수 설정."""
    global driver
    options = Options()
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.set_window_size(1920, 1080)

def naver_login():
    """네이버와 스토어에 로그인."""
    driver.get("https://www.naver.com/")
    app.logger.info('페이지 띄워짐')
    time.sleep(2)

    login_button1 = driver.find_element(By.CLASS_NAME, "MyView-module__link_login___HpHMW")
    login_button1.click()
    time.sleep(2)
    app.logger.info('로그인 버튼 클릭')

    id_input = driver.find_element(By.ID, "id")
    id_input.click()
    pyperclip.copy("althcjswo11")
    actions = ActionChains(driver)
    actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
    time.sleep(3)
    app.logger.info('아이디 입력됨')

    pw_input = driver.find_element(By.ID, "pw")
    pw_input.click()
    pyperclip.copy("alth9524!!")

    actions = ActionChains(driver)
    actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
    app.logger.info('패스워드 입력됨')
    time.sleep(3)
    pw_input.send_keys(Keys.ENTER)
    app.logger.info('엔터 입력됨')
    time.sleep(3)  # 수동으로 로그인 대기

    driver.execute_script("window.open('https://accounts.commerce.naver.com/login?url=https%3A%2F%2Fsell.smartstore.naver.com%2F%23%2Flogin-callback');")
    driver.switch_to.window(driver.window_handles[1])
    app.logger.info('스토어창 열림')
    time.sleep(2)
    login_button2 = driver.find_element(By.CLASS_NAME, "Login_btn_login__2TtMz")
    login_button2.click()
    app.logger.info('간편로그인 누름')

def get_search_data(keyword):
    """키워드를 이용해 검색 데이터를 가져옴."""
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

@app.route('/', methods=['GET'])
def index():
    global driver

    if driver is None:
        initialize_driver()

    if not driver.current_url.startswith("https://sell.smartstore.naver.com"):
        naver_login()

    return render_template('index.html', data=None)

@app.route('/api/<keyword>', methods=['GET'])
def api(keyword):
    global driver
    if driver is None:
        initialize_driver()

    # API 요청에 대해 별도 쓰레드로 처리
    thread = threading.Thread(target=get_search_data, args=(keyword,))
    thread.start()
    thread.join()  # 필요시 join() 사용해 대기
    data = get_search_data(keyword)

    return jsonify(data)

def scheduled_task():
    """주기적으로 실행할 작업."""
    app.logger.info('스케줄러 작업 실행 중...')
    keyword = "example"  # 예시로 사용할 키워드

    # 스케줄 작업을 쓰레드로 비동기 처리
    thread = threading.Thread(target=get_search_data, args=(keyword,))
    thread.start()

    # 쓰레드 종료 후 데이터 처리 로그
    app.logger.info("검색된 데이터가 스레드에서 처리되었습니다.")

def handle_job_event(event):
    """작업 완료 후 로그 처리."""
    if event.exception:
        app.logger.error(f"작업 실행 중 에러 발생: {event.job_id}")
    else:
        app.logger.info(f"작업 {event.job_id}이(가) 성공적으로 실행되었습니다.")

if __name__ == '__main__':
    # APScheduler 설정
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_task, 'interval', seconds=3, id='test_job', max_instances=1)  # 3초 간격으로 실행
    scheduler.add_listener(handle_job_event, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    # 서버 시작 시 스케줄러 시작
    scheduler.start()

    # Flask 서버 실행, use_reloader=False로 설정하여 두 번 실행되지 않도록 방지
    app.run(debug=False, use_reloader=False)

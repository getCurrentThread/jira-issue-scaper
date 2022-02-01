import json
import os
import zipfile
import urllib.request
import time
from time import sleep
from urllib import parse
import pandas as pd

from get_chrome_driver import GetChromeDriver
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# 상수 설정
COLUMNS_COUNT = 7  # 진행 중, 할 일, 완료, 담당(합), 생성, 서브태스크, 스토리포인트
ISSUE_INDEX = {'진행 중': 0, '할 일': 1, '완료': 2, '담당': 3, '생성': 4, '세분화': 5, '포인트': 6}
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, 'download')

# URL 정보 설정
# LOGIN_URL = f'https://<지라_로그인_사이트>'
# JIRA_URL = f'https://<지라_메인_사이트>'

nn_mappings: dict[str, str] = {}  # 닉네임과 이름 매핑
sm_mappings: dict[str, str] = {}
members: dict[str, list] = {}
reports = []

get_driver = GetChromeDriver()
get_driver.install()

# 팀 정보 로드
with open('members.csv') as fp:
    for line in fp:
        if not line.strip():
            break
        project_id, realname, nickname = line.strip().split(',')[:3]
        sm_mappings[realname] = project_id
        members[realname] = [0 for i in range(COLUMNS_COUNT)]
        members[realname][6] = 0.0
        nn_mappings[nickname] = realname

# 미할당 인원을 위한 더미 데이터
nn_mappings[0] = "미할당"
members[nn_mappings[0]] = [0 for i in range(COLUMNS_COUNT)]

# 다운로드 폴더 경로 만들기
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# 코치 로그인 정보 로드
secrets = json.loads(open('secrets.json').read())
COACH_ID = secrets['COACH_ID']
COACH_PASSWORD = secrets['COACH_PASSWORD']
# # 웹 드라이버 설정
#
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": DOWNLOAD_DIR,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})
# chrome_options.add_argument('--headless')  # 화면 로드 설정(주석처리하면 안뜸)
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# 웹 드라이버 객체 생성
driver = webdriver.Chrome(options=chrome_options)
url = LOGIN_URL
driver.get(url)
sleep(2)
driver.implicitly_wait(10)
driver.find_element_by_css_selector('#userId').send_keys(COACH_ID)
driver.find_element_by_css_selector('#userPwd').send_keys(COACH_PASSWORD)
driver.find_element_by_css_selector('#userPwd').send_keys(Keys.ENTER)
sleep(1)
driver.implicitly_wait(10)

url = JIRA_URL + f"/secure/MyJiraHome.jspa"
driver.get(url)
sleep(1)
driver.implicitly_wait(10)

url = JIRA_URL
    + f'/issues/?jql=' + parse.quote(
    "project in (" + ', '.join(set(sm_mappings.values())) + ")")
driver.get(url)
sleep(1)
driver.implicitly_wait(30)

url = JIRA_URL
      + f'/sr/jira.issueviews:searchrequest-csv-all-fields/temp/SearchRequest.csv?jqlQuery=' \
      + parse.quote("project in (" + ', '.join(set(sm_mappings.values())) + ")") \
      + "&delimiter=,"
driver.get(url)
sleep(1)
driver.implicitly_wait(30)

def check_if_download_folder_has_unfinished_files():
    for (dirpath, dirnames, filenames) in os.walk(DOWNLOAD_DIR):
        return str(filenames)


def wait_for_files_to_download():
    time.sleep(5)  # let the driver start downloading
    file_list = check_if_download_folder_has_unfinished_files()
    while 'Unconfirmed' in file_list or 'crdownload' in file_list:
        file_list = check_if_download_folder_has_unfinished_files()
        time.sleep(1)


wait_for_files_to_download()
driver.quit()
filepath = os.path.join(DOWNLOAD_DIR, os.listdir(DOWNLOAD_DIR)[-1])

# 다운로드한 Jira 보고서를 읽어들여 처리
data = pd.read_csv(filepath)
data = data[["프로젝트 키", "이슈 키", "이슈 유형", "상태", "담당자", "만든사람", "사용자정의 필드 (Story Points)"]]
data = data.rename(columns={"프로젝트 키": "project",
                            "이슈 키": "issue",
                            "이슈 유형": "type",
                            "상태": "status",
                            "담당자": "managed",
                            "만든사람": "created",
                            "사용자정의 필드 (Story Points)": "point"
                            }
                   )
data = data.fillna(0)

for index, row in data.iterrows():
    managed, created = nn_mappings[row['managed']], nn_mappings[row['created']]

    # 카운트업
    members[managed][ISSUE_INDEX['담당']] += 1
    members[managed][ISSUE_INDEX[row['status']]] += 1
    members[created][ISSUE_INDEX['생성']] += 1
    members[managed][ISSUE_INDEX['포인트']] += float(row['point'])

    if row['type'] == '부작업':
        members[created][ISSUE_INDEX['세분화']] += 1

# 데이터 기록
with open('jira_issue_result.csv', 'w') as fp:
    fp.write('이름, 진행 중, 할 일, 완료, 담당(합), 생성, 서브태스크, 스토리포인트\n')
    for name, value in list(members.items()):
        line = name + ", " + ", ".join(map(str, value)) + '\n'
        fp.write(line)

exit(0)

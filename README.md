# Jira Issue Scraper

Jira 보고서를 생성하여 빠르게 지라 현황 파악을 할 수 있는 생성툴

- 제작 : 곽온겸 (AntBean94)
  - origin : https://github.com/AntBean94/jira_issue_scrapper
- 수정 : 현진혁 (getCurrentThread)

### 0. 환경설정

- python 가상환경 설정 	

  ```bash
  $ python -m venv venv
  ```

- 라이브러리 설치

  ```bash
  $ pip install -r requirments.txt
  ```



### 1. 정보 입력

- 필요한 파일 목록

  ```
  1. secrets.json    --- 사용자 계정 정보
  2. members.csv     --- 이슈 스크래핑 대상자 명단
  ```

- **secrets.json**

  ```json
  {
      "COACH_ID" : "아이디",
      "COACH_PASSWORD" : "패스워드"
  }
  ```

- **members.csv**

  ```text
  지라프로젝트ID,본명,닉네임
  S00P11A222,홍길동,aaa111 
  S00P11A222,김철수,bbb222
    :
    :
    :
    :
  S00P11A223,제이슨본,born999
  ```



### 2. 실행 방법

```bash
$ python jira_issue_scrap.py
```



### 3. 결과물(예시)

| 이름     | 진행 중 | 할 일 | 완료 | 생성 | 담당 | 서브태스크 | 스토리 포인트 |
| -------- | ------- | ----- | ---- | ---- | ---- | ---------- | -------------- |
| 홍길동   | 6       | 12    | 0    | 18   | 20   | 2          | 16             |
| 김철수   | 9       | 63    | 6    | 78   | 14   | 29         | 183            |
| ...      |         |       |      |      |      |            |                |
| 제이슨본 | 2       | 36    | 9    | 47   | 35   | 13         | 97             |



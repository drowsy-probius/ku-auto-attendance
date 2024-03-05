# 블랙보드 자동출석

## Dependencies

`>=Python 3.9`

## Configuration

```yaml
# config.yaml

webhook:
  # 알림 전송할 웹훅 주소. 없으면 전송하지 않음
  - type: "discord"
    url: "https://discord.com/api/webhooks/1234567890/ABCDEFGHIJKLMN"
  - type: "slack"
    url: "https://hooks.slack.com/services/1234567890/ABCDEFGHIJKLMN"

courses:
  - name: "인권과성평등교육"
    # 과목 구분하기 위한 이름. 아무 값이나 상관 없음.

    course_id: "20771R0136ABCE12300"
    # {년도}{학기1|2}R{0136?}{학수번호}{분반} 포맷
    # https://kulms.korea.ac.kr/ultra/course
    # 위 주소에서 표시되는 강의 명 위의 회색 문자열

    course_pk: "123987"
    # [0-9]{6}
    # 강의 세부 페이지 주소에서 알아낼 수 있음
    # https://kulms.korea.ac.kr/ultra/courses/_{이부분}_1/cl/outline

    firstname: "김이박"
    # 블랙보드에 등록된 이름

    course_name: "212R [서울-학부]한글강의명(English CourseName)-00분반"
    # 블랙보드에 등록된 강의 전체 이름

    campus_nm: "안암"
    # 해당 강의가 속한 캠퍼스 이름
    # 안암 이외의 값은 확인하지 못함

    faculty: "학부"
    # 해당 강의 구분자
    # 학부 이외의 값은 확인하지 못함

    user_id: "20111180000"
    # 블랙보드 사용자 학번

    department: "ㅇㅇㅇ학과"
    # 해당 강의가 속한 학과 이름
    # 정확하지 않음

    schedule:
      # 언제 출석 요청할지에 관한 값

      start_date: "2077-03-02"
      # 출석 요청 시작일

      end_date: "2077-06-20"
      # 출석 요청 종료일

      when:
        # 어느 요일과 시간에 요청할지에 관한 값

        - day_of_week: 1
          # 0: 일요일, 1: 월요일, 2: 화요일, 3: 수요일, 4: 목요일, 5: 금요일, 6: 토요일

          start_time: "0900"
          # 강의 시작 시간 HHMM
          # 끝자리가 0 또는 5로 끝나야 함

          end_time: "1020"
          # 강의 종료 시간 HHMM
          # 끝자리가 0 또는 5로 끝나야 함
          # 실제 종료 시간보다 +5분으로 설정하는 것이 좋음

        - day_of_week: 3
          start_time: "0900"
          end_time: "1020"
```

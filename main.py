import math
from datetime import datetime
from typing import Tuple, Optional

import yaml
import requests

from utils import get_of, send_message

with open("./config.yml", "r", encoding="utf8") as ymlfile:
    cfg = yaml.safe_load(ymlfile)
webhooks = get_of(cfg, "webhooks", default=[], ignore=True)


def get_scheduled_time(
    schedule: dict, yyyymmdd: str, hhmm: str, weekday: int
) -> Optional[Tuple[str, str]]:
    start_date = get_of(schedule, "start_date")
    end_date = get_of(schedule, "end_date")

    if not start_date <= yyyymmdd <= end_date:
        return None

    for course_day in get_of(schedule, "when"):
        day_of_week = get_of(course_day, "day_of_week")
        start_time = get_of(course_day, "start_time")
        end_time = get_of(course_day, "end_time")
        if day_of_week == weekday and start_time == hhmm:
            return (start_time, end_time)

    return None


def request_attendance(
    attendance_url: str,
    course_id: str,
    course_pk: str,
    firstname: str,
    course_name: str,
    campus_nm: str,
    faculty: str,
    user_id: str,
    department: str,
    yyyymmdd: str,
    start_time_hhmm: str,
    end_time_hhmm: str,
) -> requests.Response:
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    if "-" not in yyyymmdd:
        yyyymmdd = f"{yyyymmdd[:4]}-{yyyymmdd[4:6]}-{yyyymmdd[6:8]}"
    if ":" not in start_time_hhmm:
        start_time_hhmm = f"{start_time_hhmm[:2]}:{start_time_hhmm[2:4]}"
    if ":" not in end_time_hhmm:
        end_time_hhmm = f"{end_time_hhmm[:2]}:{end_time_hhmm[2:4]}"

    data = {
        "course_id": course_id,
        "course_pk": course_pk,
        "firstname": firstname,
        "course_name": course_name,
        "campus_nm": campus_nm,
        "faculty": faculty,
        "user_id": user_id,
        "department": department,
        "class_st": f"{yyyymmdd} {start_time_hhmm}:00",
        "class_en": f"{yyyymmdd} {end_time_hhmm}:00",
    }

    response = requests.post(attendance_url, headers=headers, data=data, timeout=60)
    return response


def parse_attendance_result(response: requests.Response) -> Tuple[bool, str]:
    if not response.ok:
        return False, f"출석 요청 실패: {response.text}"

    raw_text = response.text
    try:
        data = response.json()
    except Exception as e:
        return False, f"JSON 파싱 실패: {e}\n{raw_text}"

    error_code = get_of(data, "error_code", ignore=True, default=None)
    atd_time = get_of(data, "atdTime", ignore=True, default=None)
    if error_code:
        if error_code == "103":
            return False, f"이미 출석되었습니다. 확인된 시간: {atd_time}"
        return False, f"알 수 없는 오류로 출석 실패: {error_code}\n{raw_text}"

    success_code = get_of(data, "success_code", ignore=True, default=None)
    now_time = get_of(data, "nowTime", ignore=True, default=None)
    if success_code == "success":
        return True, f"출석 성공. 요청 시간: {now_time}"
    return False, f"알 수 없는 오류로 출석 실패: {raw_text}"


def get_attendance_check_url(course_pk: str):
    return (
        "https://kulms.korea.ac.kr"
        + "/webapps/bbgs-AttendantManagementSystem-BB5d3914f35b4ad/onlineAttend/student/proc"
        + "?refreshCourseMenu=true&sortDir=ASCENDING&showAll=true"
        + "&editPaging=false&mode=view&startIndex=0"
        + f"&course_id=_{course_pk}_1"
    )


def main():
    blackboard_host = get_of(cfg, ["blackboard", "host"])
    blackboard_path = get_of(cfg, ["blackboard", "path"])
    attendance_url = f"{blackboard_host}{blackboard_path}"

    now = datetime.now()
    yyyymmdd = now.strftime("%Y-%m-%d")
    hhmm_raw = now.strftime("%H%M")
    hhmm = str(5 * math.floor(int(hhmm_raw) / 5)).zfill(4)  # 5분 단위로 내림
    weekday = now.weekday()

    for course in get_of(cfg, "courses"):
        schedule = get_of(cfg, "schedule")
        scheduled_time = get_scheduled_time(schedule, yyyymmdd, hhmm, weekday)
        if scheduled_time is None:
            continue

        start_time, end_time = scheduled_time
        course_id = get_of(course, "course_id")
        course_pk = get_of(course, "course_pk")
        firstname = get_of(course, "firstname")
        course_name = get_of(course, "course_name")
        campus_nm = get_of(course, "campus_nm")
        faculty = get_of(course, "faculty")
        user_id = get_of(course, "user_id")
        department = get_of(course, "department")

        if firstname == "테스트":
            send_message(webhooks, f"테스트 출석: {course_name}")

        res = request_attendance(
            attendance_url=attendance_url,
            course_id=course_id,
            course_pk=course_pk,
            firstname=firstname,
            course_name=course_name,
            campus_nm=campus_nm,
            faculty=faculty,
            user_id=user_id,
            department=department,
            yyyymmdd=yyyymmdd,
            start_time_hhmm=start_time,
            end_time_hhmm=end_time,
        )
        is_success, message = parse_attendance_result(res)
        status_check_url = get_attendance_check_url(course_pk)
        message = ("✅" if is_success else "🚫") + "\n" + message
        message += f"\n여기서 출석 확인\n{status_check_url}"
        send_message(webhooks, message)


if __name__ == "__main__":
    main()

"""
Strava API로 특정 날짜의 활동 찾기 및 다운로드
"""
import os
import json
import requests
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

load_dotenv()

STRAVA_ACCESS_TOKEN = os.getenv('STRAVA_ACCESS_TOKEN')


def get_recent_activities(per_page=30):
    """최근 활동 목록 조회"""
    print(f"\n{'='*60}")
    print(f"Strava API: 최근 활동 조회")
    print(f"{'='*60}\n")

    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {"Authorization": f"Bearer {STRAVA_ACCESS_TOKEN}"}
    params = {"per_page": per_page}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        activities = response.json()
        print(f"✅ 총 {len(activities)}개 활동 발견\n")

        return activities

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("❌ 인증 오류: Access Token이 만료되었습니다.")
            print("   refresh_strava_token.py를 실행하여 토큰을 갱신하세요.")
        else:
            print(f"❌ Strava API 오류: {e}")
        return None
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return None


def find_activity_by_date(activities, target_date):
    """특정 날짜의 활동 찾기"""
    print(f"{'='*60}")
    print(f"날짜 필터링: {target_date}")
    print(f"{'='*60}\n")

    matched_activities = []

    for activity in activities:
        activity_date = activity['start_date'][:10]  # YYYY-MM-DD

        if activity_date == target_date:
            matched_activities.append(activity)
            name = activity['name']
            activity_type = activity['type']
            distance = activity.get('distance', 0) / 1000
            duration = activity.get('moving_time', 0) / 60

            print(f"✅ 발견!")
            print(f"   이름: {name}")
            print(f"   타입: {activity_type}")
            print(f"   거리: {distance:.2f} km")
            print(f"   시간: {duration:.1f} 분")
            print(f"   ID: {activity['id']}")
            print()

    if not matched_activities:
        print(f"❌ {target_date} 날짜의 활동을 찾을 수 없습니다.")
        print("\n📋 전체 활동 목록:")
        for i, activity in enumerate(activities[:10], 1):
            date = activity['start_date'][:10]
            name = activity['name']
            print(f"  {i}. [{date}] {name}")

    return matched_activities


def get_activity_detail(activity_id):
    """활동 상세 정보 가져오기"""
    url = f"https://www.strava.com/api/v3/activities/{activity_id}"
    headers = {"Authorization": f"Bearer {STRAVA_ACCESS_TOKEN}"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_activity_streams(activity_id):
    """활동 스트림 데이터 가져오기"""
    url = f"https://www.strava.com/api/v3/activities/{activity_id}/streams"
    headers = {"Authorization": f"Bearer {STRAVA_ACCESS_TOKEN}"}

    stream_types = [
        'time', 'latlng', 'distance', 'altitude', 'velocity_smooth',
        'heartrate', 'cadence', 'watts', 'temp', 'moving', 'grade_smooth'
    ]
    params = {"keys": ','.join(stream_types), "key_by_type": True}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def save_activity_as_json(activity_id, output_dir="strava_data"):
    """활동을 JSON 파일로 저장"""
    print(f"\n{'='*60}")
    print(f"JSON 파일로 저장")
    print(f"{'='*60}\n")

    # 출력 디렉토리 생성
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # 활동 메타데이터
    print("활동 상세 정보 가져오는 중...")
    activity = get_activity_detail(activity_id)

    date = activity['start_date'][:10]
    name = activity['name'].replace('/', '-').replace(' ', '_')

    # 스트림 데이터
    print("스트림 데이터 가져오는 중...")
    try:
        streams = get_activity_streams(activity_id)
        print(f"✅ 스트림 데이터: {len(streams)}개 타입")
        for stream_name, stream_data in streams.items():
            points = len(stream_data.get('data', []))
            print(f"  - {stream_name}: {points:,} 포인트")
    except Exception as e:
        print(f"⚠️  스트림 데이터 가져오기 실패: {e}")
        streams = {}

    # JSON 생성
    output_data = {
        'activity': activity,
        'streams': streams,
        'downloaded_at': datetime.now().isoformat()
    }

    # 저장
    filename = output_path / f"{date}_{name}_activity.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    file_size = filename.stat().st_size
    print(f"\n✅ 저장 완료!")
    print(f"   파일: {filename}")
    print(f"   크기: {file_size:,} bytes ({file_size/1024:.1f} KB)")

    return filename


def main():
    """메인 실행"""
    print("="*60)
    print("Strava API - 12월 11일 활동 다운로드")
    print("="*60)

    # 1. 최근 활동 조회
    activities = get_recent_activities(per_page=30)

    if not activities:
        return

    # 2. 12월 11일 활동 찾기
    target_date = "2025-12-11"  # YYYY-MM-DD 형식
    matched = find_activity_by_date(activities, target_date)

    if not matched:
        print("\n다른 날짜를 시도하시려면 스크립트를 수정하세요.")
        return

    # 3. 활동 선택 (여러 개면 선택)
    if len(matched) == 1:
        selected = matched[0]
        print(f"활동 선택: {selected['name']}")
    else:
        print(f"\n{len(matched)}개의 활동이 있습니다. 선택하세요:")
        for i, act in enumerate(matched, 1):
            print(f"{i}. {act['name']} ({act['type']})")

        choice = int(input("\n번호 선택: "))
        selected = matched[choice - 1]

    # 4. JSON으로 저장
    activity_id = selected['id']
    filename = save_activity_as_json(activity_id)

    print(f"\n🎉 완료! JSON 파일이 저장되었습니다.")
    print(f"   위치: {filename}")


if __name__ == "__main__":
    main()

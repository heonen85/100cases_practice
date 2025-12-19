"""
특정 Strava 활동을 JSON으로 다운로드
"""
import os
import json
import requests
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

load_dotenv()

STRAVA_ACCESS_TOKEN = os.getenv('STRAVA_ACCESS_TOKEN')


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
    print(f"활동 다운로드: ID {activity_id}")
    print(f"{'='*60}\n")

    # 출력 디렉토리 생성
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # 활동 메타데이터
    print("활동 상세 정보 가져오는 중...")
    activity = get_activity_detail(activity_id)

    date = activity['start_date'][:10]
    name = activity['name'].replace('/', '-').replace(' ', '_')

    print(f"✅ 활동: {activity['name']}")
    print(f"   날짜: {date}")
    print(f"   타입: {activity['type']}")
    print(f"   거리: {activity.get('distance', 0)/1000:.2f} km")

    # 스트림 데이터
    print("\n스트림 데이터 가져오는 중...")
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


if __name__ == "__main__":
    # MyWhoosh - Sweetspot #1 활동 다운로드
    activity_id = 16712292810
    filename = save_activity_as_json(activity_id)
    print(f"\n🎉 완료! JSON 파일이 저장되었습니다.")

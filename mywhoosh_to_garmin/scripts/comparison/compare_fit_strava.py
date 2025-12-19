"""
FIT 파일과 Strava API 데이터 비교 스크립트
"""
import os
import requests
from dotenv import load_dotenv
from datetime import datetime
import json

# 환경 변수 로드
load_dotenv()

STRAVA_ACCESS_TOKEN = os.getenv('STRAVA_ACCESS_TOKEN')

def analyze_fit_file(fit_file_path):
    """FIT 파일 분석 (fitparse 사용)"""
    try:
        from fitparse import FitFile

        print(f"\n{'='*60}")
        print(f"FIT 파일 분석: {fit_file_path}")
        print(f"{'='*60}\n")

        fitfile = FitFile(fit_file_path)

        # 파일 크기
        file_size = os.path.getsize(fit_file_path)
        print(f"파일 크기: {file_size:,} bytes ({file_size/1024:.1f} KB)")

        # 데이터 필드 수집
        data_types = set()
        record_count = 0

        for record in fitfile.get_messages():
            if record.name == 'record':
                record_count += 1
                for field in record:
                    data_types.add(field.name)

        print(f"\n총 레코드 수: {record_count:,}")
        print(f"\n포함된 데이터 필드 ({len(data_types)}개):")
        for field in sorted(data_types):
            print(f"  - {field}")

        return {
            'file_size': file_size,
            'record_count': record_count,
            'data_fields': sorted(data_types)
        }

    except ImportError:
        print("❌ fitparse 라이브러리가 설치되지 않았습니다.")
        print("설치: pip install fitparse")
        return None
    except Exception as e:
        print(f"❌ FIT 파일 분석 오류: {e}")
        return None


def get_strava_activities(limit=10):
    """Strava에서 최근 활동 목록 가져오기"""
    print(f"\n{'='*60}")
    print(f"Strava API: 최근 활동 조회")
    print(f"{'='*60}\n")

    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {"Authorization": f"Bearer {STRAVA_ACCESS_TOKEN}"}
    params = {"per_page": limit}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        activities = response.json()

        print(f"총 {len(activities)}개 활동 발견:\n")
        for i, activity in enumerate(activities, 1):
            date = activity['start_date'][:10]
            name = activity['name']
            activity_type = activity['type']
            distance = activity.get('distance', 0) / 1000  # km

            print(f"{i}. [{date}] {name} ({activity_type}) - {distance:.1f}km")
            print(f"   ID: {activity['id']}")

        return activities

    except requests.exceptions.RequestException as e:
        print(f"❌ Strava API 오류: {e}")
        return None


def get_strava_activity_streams(activity_id):
    """특정 활동의 스트림 데이터 가져오기"""
    print(f"\n{'='*60}")
    print(f"Strava API: 활동 스트림 데이터 조회 (ID: {activity_id})")
    print(f"{'='*60}\n")

    url = f"https://www.strava.com/api/v3/activities/{activity_id}/streams"
    headers = {"Authorization": f"Bearer {STRAVA_ACCESS_TOKEN}"}

    # 모든 가능한 스트림 타입 요청
    stream_types = [
        'time', 'latlng', 'distance', 'altitude', 'velocity_smooth',
        'heartrate', 'cadence', 'watts', 'temp', 'moving', 'grade_smooth'
    ]
    params = {"keys": ','.join(stream_types), "key_by_type": True}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        streams = response.json()

        print(f"사용 가능한 스트림 데이터 ({len(streams)}개):")
        for stream_name, stream_data in streams.items():
            data_points = len(stream_data.get('data', []))
            print(f"  - {stream_name}: {data_points:,} 포인트")

        return streams

    except requests.exceptions.RequestException as e:
        print(f"❌ Strava Streams API 오류: {e}")
        if response.status_code == 404:
            print("활동을 찾을 수 없습니다. ID를 확인하세요.")
        return None


def compare_data(fit_data, strava_streams):
    """FIT 파일과 Strava 데이터 비교"""
    print(f"\n{'='*60}")
    print(f"데이터 비교 분석")
    print(f"{'='*60}\n")

    if not fit_data or not strava_streams:
        print("비교할 데이터가 없습니다.")
        return

    # FIT 필드 vs Strava 스트림 매핑
    field_mapping = {
        'heart_rate': 'heartrate',
        'cadence': 'cadence',
        'power': 'watts',
        'temperature': 'temp',
        'altitude': 'altitude',
        'speed': 'velocity_smooth',
        'distance': 'distance',
        'position_lat': 'latlng',
        'position_long': 'latlng',
    }

    print("필드별 비교:\n")

    fit_fields = set(fit_data['data_fields'])
    strava_fields = set(strava_streams.keys())

    print("✅ FIT 파일에 있고 Strava에도 있는 데이터:")
    for fit_field, strava_field in field_mapping.items():
        if fit_field in fit_fields and strava_field in strava_fields:
            print(f"  - {fit_field} ↔ {strava_field}")

    print("\n⚠️  FIT 파일에는 있지만 Strava에 없는 데이터:")
    missing_in_strava = []
    for fit_field in fit_fields:
        matched = False
        for fit_key, strava_key in field_mapping.items():
            if fit_field == fit_key and strava_key in strava_fields:
                matched = True
                break
        if not matched and fit_field not in ['timestamp', 'unknown']:
            missing_in_strava.append(fit_field)
            print(f"  - {fit_field}")

    print("\n📊 데이터 손실 평가:")
    total_fields = len(fit_fields)
    preserved_fields = len([f for f in field_mapping.keys() if f in fit_fields and field_mapping[f] in strava_fields])

    if total_fields > 0:
        preservation_rate = (preserved_fields / total_fields) * 100
        print(f"  보존률: {preservation_rate:.1f}% ({preserved_fields}/{total_fields} 필드)")

    if 'power' in fit_fields and 'watts' not in strava_fields:
        print("\n  ⚠️  주요 손실: 파워 데이터 (watts) - 사이클링에 중요!")

    if 'heart_rate' in fit_fields and 'heartrate' not in strava_fields:
        print("  ⚠️  주요 손실: 심박수 데이터")


def main():
    print("\n" + "="*60)
    print("FIT 파일 vs Strava API 데이터 비교")
    print("="*60)

    # 1. FIT 파일 분석
    fit_file = "MyWhoosh_Sweetspot_1.fit"
    fit_data = analyze_fit_file(fit_file)

    # 2. Strava 활동 목록 조회
    activities = get_strava_activities(limit=5)

    if not activities:
        print("\n프로그램을 종료합니다.")
        return

    # 3. 사용자에게 활동 선택 요청
    print(f"\n어떤 활동을 비교하시겠습니까?")
    print("활동 번호를 입력하세요 (1-5): ", end="")

    try:
        choice = int(input())
        if 1 <= choice <= len(activities):
            selected_activity = activities[choice - 1]
            activity_id = selected_activity['id']

            # 4. 선택한 활동의 스트림 데이터 가져오기
            strava_streams = get_strava_activity_streams(activity_id)

            # 5. 비교 분석
            compare_data(fit_data, strava_streams)

            # 6. 결과 저장
            result = {
                'fit_file': fit_file,
                'fit_data': fit_data,
                'strava_activity': {
                    'id': activity_id,
                    'name': selected_activity['name'],
                    'date': selected_activity['start_date']
                },
                'strava_streams': list(strava_streams.keys()) if strava_streams else [],
                'timestamp': datetime.now().isoformat()
            }

            with open('comparison_result.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            print(f"\n결과가 comparison_result.json에 저장되었습니다.")
        else:
            print("잘못된 선택입니다.")

    except ValueError:
        print("숫자를 입력하세요.")
    except KeyboardInterrupt:
        print("\n\n프로그램을 종료합니다.")


if __name__ == "__main__":
    main()

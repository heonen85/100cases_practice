"""
JSON (Strava API) vs FIT (원본 파일) 비교 스크립트

사용 사례:
1. Strava API로 백업한 JSON 파일이 원본 FIT 데이터를 잘 보존하는지 확인
2. 데이터 손실 여부 확인
3. 어느 형식이 더 많은 정보를 담고 있는지 비교
"""
import json
from pathlib import Path
from datetime import datetime


def analyze_json_file(json_path):
    """JSON 파일 분석 (Strava API 데이터)"""
    print(f"\n{'='*60}")
    print(f"JSON 파일 분석: {json_path}")
    print(f"{'='*60}\n")

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 파일 크기
    file_size = Path(json_path).stat().st_size
    print(f"파일 크기: {file_size:,} bytes ({file_size/1024:.1f} KB)")

    # 메타데이터
    activity = data.get('activity', {})
    print(f"\n📋 메타데이터:")
    print(f"  이름: {activity.get('name')}")
    print(f"  날짜: {activity.get('start_date')}")
    print(f"  타입: {activity.get('type')}")
    print(f"  거리: {activity.get('distance', 0)/1000:.2f} km")
    print(f"  소요 시간: {activity.get('moving_time', 0)/60:.1f} 분")
    print(f"  평균 속도: {activity.get('average_speed', 0)*3.6:.1f} km/h")

    # 스트림 데이터
    streams = data.get('streams', {})
    if streams:
        print(f"\n📊 스트림 데이터 ({len(streams)}개 타입):")

        total_points = 0
        for stream_name, stream_data in streams.items():
            if isinstance(stream_data, dict) and 'data' in stream_data:
                data_points = len(stream_data['data'])
                total_points = max(total_points, data_points)
                print(f"  - {stream_name}: {data_points:,} 포인트")

        print(f"\n  총 데이터 포인트: {total_points:,}")
    else:
        print(f"\n⚠️  스트림 데이터 없음 (메타데이터만 포함)")
        total_points = 0

    return {
        'file_size': file_size,
        'total_points': total_points,
        'streams': list(streams.keys()) if streams else [],
        'has_metadata': bool(activity),
        'has_streams': bool(streams),
        'activity_name': activity.get('name'),
        'distance': activity.get('distance', 0),
        'duration': activity.get('moving_time', 0)
    }


def analyze_fit_file(fit_path):
    """FIT 파일 분석"""
    print(f"\n{'='*60}")
    print(f"FIT 파일 분석: {fit_path}")
    print(f"{'='*60}\n")

    try:
        from fitparse import FitFile
    except ImportError:
        print("❌ fitparse 라이브러리가 설치되지 않았습니다.")
        print("   설치: pip install fitparse")
        return None

    # 파일 크기
    file_size = Path(fit_path).stat().st_size
    print(f"파일 크기: {file_size:,} bytes ({file_size/1024:.1f} KB)")

    fitfile = FitFile(fit_path)

    # 데이터 수집
    data_fields = set()
    record_count = 0
    session_info = {}

    # Session 정보 추출
    for record in fitfile.get_messages('session'):
        for field in record:
            if field.name in ['sport', 'total_distance', 'total_elapsed_time',
                             'avg_speed', 'avg_heart_rate', 'avg_power', 'avg_cadence']:
                session_info[field.name] = field.value

    # Record 데이터 필드
    for record in fitfile.get_messages('record'):
        record_count += 1
        for field in record:
            data_fields.add(field.name)

    print(f"\n📋 세션 정보:")
    print(f"  종목: {session_info.get('sport', 'N/A')}")
    if 'total_distance' in session_info:
        print(f"  거리: {session_info['total_distance']/1000:.2f} km")
    if 'total_elapsed_time' in session_info:
        print(f"  소요 시간: {session_info['total_elapsed_time']/60:.1f} 분")
    if 'avg_speed' in session_info:
        print(f"  평균 속도: {session_info['avg_speed']*3.6:.1f} km/h")
    if 'avg_heart_rate' in session_info:
        print(f"  평균 심박수: {session_info['avg_heart_rate']:.0f} bpm")
    if 'avg_power' in session_info:
        print(f"  평균 파워: {session_info['avg_power']:.0f} watts")

    print(f"\n📊 레코드 데이터:")
    print(f"  총 레코드: {record_count:,}")
    print(f"  데이터 필드 ({len(data_fields)}개):")
    for field in sorted(data_fields):
        print(f"    - {field}")

    return {
        'file_size': file_size,
        'total_points': record_count,
        'data_fields': sorted(data_fields),
        'session_info': session_info,
        'distance': session_info.get('total_distance', 0),
        'duration': session_info.get('total_elapsed_time', 0)
    }


def compare_data(json_data, fit_data):
    """JSON과 FIT 데이터 비교"""
    print(f"\n{'='*60}")
    print(f"📊 JSON vs FIT 비교 분석")
    print(f"{'='*60}\n")

    if not json_data or not fit_data:
        print("비교할 데이터가 없습니다.")
        return

    # 1. 파일 크기 비교
    print("1️⃣ 파일 크기 비교:")
    json_size = json_data['file_size']
    fit_size = fit_data['file_size']

    print(f"  JSON: {json_size:,} bytes ({json_size/1024:.1f} KB)")
    print(f"  FIT:  {fit_size:,} bytes ({fit_size/1024:.1f} KB)")

    if json_size > fit_size:
        ratio = json_size / fit_size
        print(f"  → JSON이 {ratio:.1f}배 더 큼 (텍스트 형식이라 비효율적)")
    else:
        ratio = fit_size / json_size
        print(f"  → FIT가 {ratio:.1f}배 더 큼 (이진 형식으로 압축)")

    # 2. 데이터 포인트 수 비교
    print(f"\n2️⃣ 데이터 포인트 수 비교:")
    json_points = json_data['total_points']
    fit_points = fit_data['total_points']

    print(f"  JSON: {json_points:,} 포인트")
    print(f"  FIT:  {fit_points:,} 포인트")

    if json_points == fit_points:
        print(f"  ✅ 동일! (데이터 손실 없음)")
    elif json_points > fit_points:
        diff = json_points - fit_points
        print(f"  ⚠️  JSON이 {diff:,}개 더 많음 (보간 데이터?)")
    else:
        diff = fit_points - json_points
        print(f"  ⚠️  FIT가 {diff:,}개 더 많음 (JSON에서 {diff*100/fit_points:.1f}% 손실)")

    # 3. 데이터 필드 비교
    print(f"\n3️⃣ 데이터 필드 비교:")

    # JSON 스트림 → FIT 필드 매핑
    stream_to_field = {
        'time': 'timestamp',
        'latlng': ['position_lat', 'position_long'],
        'distance': 'distance',
        'altitude': 'altitude',
        'velocity_smooth': 'speed',
        'heartrate': 'heart_rate',
        'cadence': 'cadence',
        'watts': 'power',
        'temp': 'temperature',
        'moving': 'N/A',
        'grade_smooth': 'grade'
    }

    json_streams = set(json_data.get('streams', []))
    fit_fields = set(fit_data.get('data_fields', []))

    print(f"\n  JSON 스트림: {len(json_streams)}개")
    for stream in sorted(json_streams):
        print(f"    - {stream}")

    print(f"\n  FIT 필드: {len(fit_fields)}개")
    for field in sorted(fit_fields):
        print(f"    - {field}")

    # 매칭 분석
    print(f"\n  ✅ 양쪽 모두 있는 데이터:")
    matched = []
    for json_stream, fit_field in stream_to_field.items():
        if json_stream in json_streams:
            if isinstance(fit_field, list):
                if all(f in fit_fields for f in fit_field):
                    matched.append(json_stream)
                    print(f"    - {json_stream} ↔ {', '.join(fit_field)}")
            elif fit_field in fit_fields:
                matched.append(json_stream)
                print(f"    - {json_stream} ↔ {fit_field}")

    print(f"\n  ⚠️  FIT에만 있는 데이터 (JSON 손실):")
    fit_only = []
    for field in sorted(fit_fields):
        # timestamp, unknown 등 제외
        if field not in ['timestamp', 'unknown'] and \
           field not in [v for v in stream_to_field.values() if isinstance(v, str)] and \
           field not in [item for sublist in stream_to_field.values() if isinstance(sublist, list) for item in sublist]:
            fit_only.append(field)
            print(f"    - {field}")

    if not fit_only:
        print(f"    (없음)")

    print(f"\n  ⚠️  JSON에만 있는 데이터 (FIT에 없음):")
    json_only = []
    for stream in sorted(json_streams):
        fit_field = stream_to_field.get(stream)
        if fit_field:
            if isinstance(fit_field, list):
                if not any(f in fit_fields for f in fit_field):
                    json_only.append(stream)
                    print(f"    - {stream}")
            elif fit_field not in fit_fields:
                json_only.append(stream)
                print(f"    - {stream}")
        else:
            json_only.append(stream)
            print(f"    - {stream}")

    if not json_only:
        print(f"    (없음)")

    # 4. 통계 비교 (거리, 시간)
    print(f"\n4️⃣ 통계 비교:")
    if json_data.get('distance') and fit_data.get('distance'):
        json_dist = json_data['distance'] / 1000
        fit_dist = fit_data['distance'] / 1000
        print(f"  거리:")
        print(f"    JSON: {json_dist:.2f} km")
        print(f"    FIT:  {fit_dist:.2f} km")
        if abs(json_dist - fit_dist) < 0.1:
            print(f"    ✅ 거의 동일")
        else:
            diff = abs(json_dist - fit_dist)
            print(f"    ⚠️  차이: {diff:.2f} km")

    if json_data.get('duration') and fit_data.get('duration'):
        json_dur = json_data['duration'] / 60
        fit_dur = fit_data['duration'] / 60
        print(f"\n  소요 시간:")
        print(f"    JSON: {json_dur:.1f} 분")
        print(f"    FIT:  {fit_dur:.1f} 분")
        if abs(json_dur - fit_dur) < 1:
            print(f"    ✅ 거의 동일")
        else:
            diff = abs(json_dur - fit_dur)
            print(f"    ⚠️  차이: {diff:.1f} 분")

    # 5. 종합 평가
    print(f"\n{'='*60}")
    print(f"📝 종합 평가")
    print(f"{'='*60}\n")

    score = 0
    total = 4

    # 데이터 포인트 일치
    if abs(json_points - fit_points) / max(fit_points, 1) < 0.05:
        print("✅ 데이터 포인트 수: 거의 동일 (±5% 이내)")
        score += 1
    else:
        print("⚠️  데이터 포인트 수: 차이 있음")

    # 필드 보존율
    preservation_rate = len(matched) / max(len(json_streams), 1) * 100
    print(f"✅ 필드 보존율: {preservation_rate:.0f}%")
    if preservation_rate > 80:
        score += 1

    # 통계 일치
    if json_data.get('distance') and fit_data.get('distance'):
        dist_diff = abs(json_data['distance'] - fit_data['distance']) / max(fit_data['distance'], 1)
        if dist_diff < 0.01:
            print("✅ 거리 통계: 일치")
            score += 1
        else:
            print(f"⚠️  거리 통계: {dist_diff*100:.1f}% 차이")

    # 파일 크기 효율성
    if fit_size < json_size:
        print(f"✅ 파일 크기: FIT가 더 효율적 (JSON의 {fit_size/json_size*100:.0f}%)")
        score += 1
    else:
        print(f"⚠️  파일 크기: JSON이 비효율적")

    print(f"\n종합 점수: {score}/{total}")

    if score == total:
        print("🎉 완벽! JSON이 FIT 데이터를 잘 보존하고 있습니다.")
    elif score >= total * 0.7:
        print("👍 양호. 대부분의 데이터가 보존되었습니다.")
    else:
        print("⚠️  주의. 데이터 손실이 있을 수 있습니다.")


def main():
    """메인 실행"""
    print("="*60)
    print("JSON (Strava API) vs FIT (원본) 비교")
    print("="*60)

    # 파일 경로 입력
    print("\n비교할 파일을 입력하세요:")
    json_path = input("JSON 파일 경로: ").strip()
    fit_path = input("FIT 파일 경로: ").strip()

    # 파일 존재 확인
    if not Path(json_path).exists():
        print(f"❌ JSON 파일을 찾을 수 없습니다: {json_path}")
        return

    if not Path(fit_path).exists():
        print(f"❌ FIT 파일을 찾을 수 없습니다: {fit_path}")
        return

    # 분석
    json_data = analyze_json_file(json_path)
    fit_data = analyze_fit_file(fit_path)

    # 비교
    if json_data and fit_data:
        compare_data(json_data, fit_data)

        # 결과 저장
        result = {
            'json_file': str(json_path),
            'fit_file': str(fit_path),
            'json_analysis': json_data,
            'fit_analysis': fit_data,
            'timestamp': datetime.now().isoformat()
        }

        output_file = 'json_fit_comparison_result.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"\n결과가 {output_file}에 저장되었습니다.")


if __name__ == "__main__":
    main()

"""
Strava API 데이터 저장 스크립트
여러 형식으로 활동 데이터를 저장할 수 있습니다.
"""
import os
import json
import csv
import requests
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path

load_dotenv()

STRAVA_ACCESS_TOKEN = os.getenv('STRAVA_ACCESS_TOKEN')


class StravaDataSaver:
    """Strava API 데이터를 여러 형식으로 저장"""

    def __init__(self):
        self.headers = {"Authorization": f"Bearer {STRAVA_ACCESS_TOKEN}"}
        self.output_dir = Path("strava_data")
        self.output_dir.mkdir(exist_ok=True)

    def get_activity_detail(self, activity_id):
        """활동 상세 정보 가져오기"""
        url = f"https://www.strava.com/api/v3/activities/{activity_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_activity_streams(self, activity_id):
        """활동 스트림 데이터 가져오기"""
        url = f"https://www.strava.com/api/v3/activities/{activity_id}/streams"
        stream_types = [
            'time', 'latlng', 'distance', 'altitude', 'velocity_smooth',
            'heartrate', 'cadence', 'watts', 'temp', 'moving', 'grade_smooth'
        ]
        params = {"keys": ','.join(stream_types), "key_by_type": True}

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    # ==================== 저장 방법 1: JSON 파일 ====================
    def save_as_json(self, activity_id, include_streams=True):
        """
        JSON 형식으로 저장

        장점:
        - 가장 간단하고 빠름
        - 모든 데이터를 그대로 보존
        - Python으로 쉽게 재사용 가능

        단점:
        - 다른 앱에서 불러올 수 없음
        - 파일 크기가 큼
        """
        print(f"\n{'='*60}")
        print(f"방법 1: JSON 파일로 저장")
        print(f"{'='*60}\n")

        # 활동 메타데이터
        activity = self.get_activity_detail(activity_id)
        date = activity['start_date'][:10]
        name = activity['name'].replace('/', '-')

        output_data = {
            'activity': activity,
            'downloaded_at': datetime.now().isoformat()
        }

        # 스트림 데이터 포함
        if include_streams:
            streams = self.get_activity_streams(activity_id)
            output_data['streams'] = streams
            print(f"✅ 스트림 데이터 포함: {len(streams)}개 타입")

        # 저장
        filename = self.output_dir / f"{date}_{name}_activity.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"✅ 저장 완료: {filename}")
        print(f"   파일 크기: {filename.stat().st_size / 1024:.1f} KB")
        return filename

    # ==================== 저장 방법 2: GPX 파일 ====================
    def save_as_gpx(self, activity_id):
        """
        GPX (GPS Exchange Format) 파일로 저장

        장점:
        - GPS 데이터 표준 형식
        - Garmin, Strava 등 대부분의 앱에서 인식
        - 구글 지도, Google Earth에서 열기 가능

        단점:
        - GPS 좌표가 없으면 생성 불가
        - 파워, 심박수 등은 확장 필드로 저장
        """
        print(f"\n{'='*60}")
        print(f"방법 2: GPX 파일로 저장")
        print(f"{'='*60}\n")

        activity = self.get_activity_detail(activity_id)
        streams = self.get_activity_streams(activity_id)

        # GPS 좌표 확인
        if 'latlng' not in streams:
            print("❌ GPS 좌표가 없어 GPX 파일을 생성할 수 없습니다.")
            print("   (실내 사이클링은 GPS 데이터가 없습니다)")
            return None

        # GPX XML 생성
        date = activity['start_date'][:10]
        name = activity['name'].replace('/', '-')
        start_time = activity['start_date']

        gpx_content = self._create_gpx_xml(activity, streams)

        # 저장
        filename = self.output_dir / f"{date}_{name}.gpx"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(gpx_content)

        print(f"✅ 저장 완료: {filename}")
        print(f"   파일 크기: {filename.stat().st_size / 1024:.1f} KB")
        return filename

    def _create_gpx_xml(self, activity, streams):
        """GPX XML 문자열 생성"""
        from xml.etree.ElementTree import Element, SubElement, tostring
        from xml.dom import minidom

        # GPX 루트
        gpx = Element('gpx', {
            'version': '1.1',
            'creator': 'Strava Data Saver',
            'xmlns': 'http://www.topografix.com/GPX/1/1',
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xmlns:gpxtpx': 'http://www.garmin.com/xmlschemas/TrackPointExtension/v1'
        })

        # 메타데이터
        metadata = SubElement(gpx, 'metadata')
        SubElement(metadata, 'name').text = activity['name']
        SubElement(metadata, 'time').text = activity['start_date']

        # 트랙
        trk = SubElement(gpx, 'trk')
        SubElement(trk, 'name').text = activity['name']
        SubElement(trk, 'type').text = activity['type']

        trkseg = SubElement(trk, 'trkseg')

        # 각 포인트 추가
        latlng_data = streams['latlng']['data']
        time_data = streams['time']['data']
        altitude_data = streams.get('altitude', {}).get('data', [])
        heartrate_data = streams.get('heartrate', {}).get('data', [])
        cadence_data = streams.get('cadence', {}).get('data', [])
        watts_data = streams.get('watts', {}).get('data', [])

        start_time = datetime.fromisoformat(activity['start_date'].replace('Z', '+00:00'))

        for i, (lat, lng) in enumerate(latlng_data):
            trkpt = SubElement(trkseg, 'trkpt', {'lat': str(lat), 'lon': str(lng)})

            # 시간
            point_time = start_time.timestamp() + time_data[i]
            time_str = datetime.fromtimestamp(point_time).isoformat() + 'Z'
            SubElement(trkpt, 'time').text = time_str

            # 고도
            if i < len(altitude_data):
                SubElement(trkpt, 'ele').text = str(altitude_data[i])

            # 확장 데이터 (심박수, 케이던스, 파워)
            if heartrate_data or cadence_data or watts_data:
                extensions = SubElement(trkpt, 'extensions')
                tpx = SubElement(extensions, 'gpxtpx:TrackPointExtension')

                if i < len(heartrate_data):
                    SubElement(tpx, 'gpxtpx:hr').text = str(int(heartrate_data[i]))
                if i < len(cadence_data):
                    SubElement(tpx, 'gpxtpx:cad').text = str(int(cadence_data[i]))
                if i < len(watts_data):
                    SubElement(tpx, 'gpxtpx:power').text = str(int(watts_data[i]))

        # 포맷팅
        rough_string = tostring(gpx, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent='  ')

    # ==================== 저장 방법 3: CSV 파일 ====================
    def save_as_csv(self, activity_id):
        """
        CSV 형식으로 저장

        장점:
        - Excel, Google Sheets에서 바로 열림
        - 데이터 분석에 용이
        - 파일 크기 작음

        단점:
        - 다른 앱에서 업로드 불가
        - 메타데이터 손실
        """
        print(f"\n{'='*60}")
        print(f"방법 3: CSV 파일로 저장")
        print(f"{'='*60}\n")

        activity = self.get_activity_detail(activity_id)
        streams = self.get_activity_streams(activity_id)

        date = activity['start_date'][:10]
        name = activity['name'].replace('/', '-')

        # CSV 헤더 생성
        headers = ['time']
        data_arrays = {'time': streams['time']['data']}

        # 사용 가능한 스트림 추가
        for stream_name, stream_data in streams.items():
            if stream_name != 'time':
                if stream_name == 'latlng':
                    headers.extend(['latitude', 'longitude'])
                    data_arrays['latitude'] = [point[0] for point in stream_data['data']]
                    data_arrays['longitude'] = [point[1] for point in stream_data['data']]
                else:
                    headers.append(stream_name)
                    data_arrays[stream_name] = stream_data['data']

        # CSV 저장
        filename = self.output_dir / f"{date}_{name}_data.csv"

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)

            # 데이터 행 작성
            num_rows = len(data_arrays['time'])
            for i in range(num_rows):
                row = []
                for header in headers:
                    if header in data_arrays and i < len(data_arrays[header]):
                        row.append(data_arrays[header][i])
                    else:
                        row.append('')
                writer.writerow(row)

        print(f"✅ 저장 완료: {filename}")
        print(f"   파일 크기: {filename.stat().st_size / 1024:.1f} KB")
        print(f"   컬럼: {', '.join(headers)}")
        return filename

    # ==================== 저장 방법 4: FIT 파일 변환 ====================
    def save_as_fit(self, activity_id):
        """
        FIT 파일로 변환하여 저장

        장점:
        - Garmin의 네이티브 형식
        - 모든 데이터 보존 (파워, 심박수 등)
        - 파일 크기 최소

        단점:
        - fitfile 라이브러리 필요
        - 변환 로직이 복잡
        - API 데이터 → FIT 변환 시 일부 정보 손실 가능
        """
        print(f"\n{'='*60}")
        print(f"방법 4: FIT 파일로 변환")
        print(f"{'='*60}\n")

        try:
            from fitfile import FitFile, Record, Activity
            print("✅ fitfile 라이브러리 사용 가능")
        except ImportError:
            print("❌ fitfile 라이브러리가 설치되지 않았습니다.")
            print("   설치: pip install fitfile")
            print("\n⚠️  대안: Strava에서 원본 FIT 파일 다운로드")
            print("   Strava는 업로드된 원본 FIT 파일을 제공하지 않습니다.")
            print("   API로는 변환된 데이터만 받을 수 있습니다.")
            return None

        # FIT 파일 생성 로직은 복잡하므로 생략
        # 실제로는 Strava에서 원본 FIT 파일을 다운로드하는 것이 더 좋습니다

    # ==================== 저장 방법 5: 원본 파일 다운로드 ====================
    def download_original_file(self, activity_id):
        """
        Strava에서 원본 파일 다운로드 (웹 스크래핑 필요)

        장점:
        - 원본 그대로 보존
        - 데이터 손실 없음

        단점:
        - API로는 불가능 (웹 스크래핑 필요)
        - 로그인 세션 관리 필요

        참고: Strava API는 원본 파일 다운로드를 지원하지 않습니다.
        """
        print(f"\n{'='*60}")
        print(f"방법 5: 원본 파일 다운로드")
        print(f"{'='*60}\n")

        print("⚠️  Strava API는 원본 파일 다운로드를 지원하지 않습니다.")
        print("\n대안:")
        print("1. 웹 브라우저에서 수동 다운로드")
        print("   - https://www.strava.com/activities/{activity_id}")
        print("   - 우측 상단 '...' → 'Export Original'")
        print("\n2. Playwright로 자동화 (MyWhoosh처럼)")
        print("   - 로그인 후 다운로드 버튼 클릭")


def main():
    """메인 실행"""
    print("="*60)
    print("Strava API 데이터 저장 방법 데모")
    print("="*60)

    # 활동 ID 입력
    print("\nStrava 활동 ID를 입력하세요:")
    print("(활동 URL: https://www.strava.com/activities/[이 숫자])")
    activity_id = input("Activity ID: ").strip()

    if not activity_id.isdigit():
        print("❌ 올바른 활동 ID를 입력하세요.")
        return

    saver = StravaDataSaver()

    # 저장 방법 선택
    print("\n어떤 형식으로 저장하시겠습니까?")
    print("1. JSON (모든 데이터 보존, Python 재사용 용이)")
    print("2. GPX (GPS 앱 호환, 지도 표시 가능)")
    print("3. CSV (Excel 분석용)")
    print("4. 모두 저장")

    choice = input("\n선택 (1-4): ").strip()

    try:
        if choice == '1':
            saver.save_as_json(activity_id)
        elif choice == '2':
            saver.save_as_gpx(activity_id)
        elif choice == '3':
            saver.save_as_csv(activity_id)
        elif choice == '4':
            print("\n모든 형식으로 저장합니다...\n")
            saver.save_as_json(activity_id)
            saver.save_as_gpx(activity_id)
            saver.save_as_csv(activity_id)
        else:
            print("잘못된 선택입니다.")

        print(f"\n✅ 완료! 저장 위치: {saver.output_dir}/")

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("\n❌ 인증 오류: Access Token이 만료되었거나 잘못되었습니다.")
            print("   refresh_strava_token.py를 실행하여 토큰을 갱신하세요.")
        elif e.response.status_code == 404:
            print(f"\n❌ 활동을 찾을 수 없습니다 (ID: {activity_id})")
        else:
            print(f"\n❌ Strava API 오류: {e}")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

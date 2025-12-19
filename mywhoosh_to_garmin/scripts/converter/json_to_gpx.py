"""
JSON 파일을 GPX로 변환하여 Garmin 업로드 가능하게 만들기
"""
import json
from pathlib import Path
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom


def json_to_gpx(json_path, output_path=None):
    """JSON 파일을 GPX로 변환"""

    print(f"\n{'='*60}")
    print(f"JSON → GPX 변환")
    print(f"{'='*60}\n")

    # JSON 읽기
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    activity = data['activity']
    streams = data.get('streams', {})

    # GPS 좌표 확인
    if 'latlng' not in streams:
        print("❌ GPS 좌표가 없어 GPX 파일을 생성할 수 없습니다.")
        print("   (실내 사이클링은 GPS 데이터가 없을 수 있습니다)")
        return None

    # 출력 경로 설정
    if not output_path:
        date = activity['start_date'][:10]
        name = activity['name'].replace('/', '-').replace(' ', '_')
        output_path = f"strava_data/{date}_{name}.gpx"

    # GPX XML 생성
    gpx = Element('gpx', {
        'version': '1.1',
        'creator': 'Strava API to GPX Converter',
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

    # 데이터 추출
    latlng_data = streams['latlng']['data']
    time_data = streams['time']['data']
    altitude_data = streams.get('altitude', {}).get('data', [])
    heartrate_data = streams.get('heartrate', {}).get('data', [])
    cadence_data = streams.get('cadence', {}).get('data', [])
    watts_data = streams.get('watts', {}).get('data', [])

    start_time = datetime.fromisoformat(activity['start_date'].replace('Z', '+00:00'))

    print(f"변환 중: {activity['name']}")
    print(f"  포인트 수: {len(latlng_data):,}")

    # 각 포인트 추가
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

    # 포맷팅 및 저장
    rough_string = tostring(gpx, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent='  ')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)

    file_size = Path(output_path).stat().st_size

    print(f"\n✅ GPX 변환 완료!")
    print(f"   파일: {output_path}")
    print(f"   크기: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    print(f"\n이제 이 GPX 파일을 Garmin Connect에 업로드할 수 있습니다:")
    print(f"   https://connect.garmin.com/modern/import-data")

    return output_path


if __name__ == "__main__":
    json_path = "strava_data/2025-12-11_MyWhoosh_-_Sweetspot_#1_activity.json"
    json_to_gpx(json_path)

#!/usr/bin/env python3
"""
MyWhoosh to Garmin Connect 동기화 스크립트
"""
import os
import sys
from datetime import datetime
from pathlib import Path

# 프로젝트 루트 디렉토리 설정
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.mywhoosh_downloader import MyWhooshDownloader
from src.garmin_uploader import GarminUploader
from src.history_manager import HistoryManager


def setup_logging():
    """로그 설정"""
    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"sync_{timestamp}.log"

    return log_file


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("MyWhoosh to Garmin Connect 동기화 시작")
    print("=" * 60)
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    log_file = setup_logging()

    # 환경 변수 확인
    mywhoosh_email = os.getenv('MYWHOOSH_EMAIL')
    mywhoosh_password = os.getenv('MYWHOOSH_PASSWORD')
    garmin_email = os.getenv('GARMIN_EMAIL')
    garmin_password = os.getenv('GARMIN_PASSWORD')

    if not all([mywhoosh_email, mywhoosh_password, garmin_email, garmin_password]):
        print("❌ 환경 변수가 설정되지 않았습니다!")
        print("필요한 환경 변수: MYWHOOSH_EMAIL, MYWHOOSH_PASSWORD, GARMIN_EMAIL, GARMIN_PASSWORD")
        return 1

    try:
        # 이력 관리자 초기화
        history = HistoryManager()

        # MyWhoosh 다운로더 초기화
        print("1️⃣  MyWhoosh 다운로드 시작...")
        downloader = MyWhooshDownloader(mywhoosh_email, mywhoosh_password)

        # 활동 다운로드 (최근 30일)
        downloaded_files = downloader.download_recent_activities(days=30)
        print(f"✅ {len(downloaded_files)}개 활동 다운로드 완료")
        print()

        if not downloaded_files:
            print("⚠️  다운로드된 새 활동이 없습니다.")
            return 0

        # Garmin 업로더 초기화
        print("2️⃣  Garmin Connect 업로드 시작...")
        uploader = GarminUploader(garmin_email, garmin_password)

        # 업로드 결과 추적
        success_count = 0
        skip_count = 0
        error_count = 0

        for file_path in downloaded_files:
            file_name = os.path.basename(file_path)

            # 이미 업로드했는지 확인
            if history.is_uploaded(file_name):
                print(f"⏭️  건너뜀: {file_name} (이미 업로드됨)")
                skip_count += 1
                continue

            # 업로드 시도
            result = uploader.upload(file_path)

            if result['success']:
                print(f"✅ 업로드 성공: {file_name}")
                history.mark_uploaded(file_name)
                success_count += 1
            elif result.get('duplicate'):
                print(f"🔄 중복: {file_name} (이미 Garmin에 존재)")
                history.mark_uploaded(file_name)
                skip_count += 1
            else:
                print(f"❌ 업로드 실패: {file_name} - {result.get('error')}")
                error_count += 1

        print()
        print("=" * 60)
        print("동기화 완료")
        print("=" * 60)
        print(f"✅ 성공: {success_count}개")
        print(f"⏭️  건너뜀: {skip_count}개")
        print(f"❌ 실패: {error_count}개")
        print(f"종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        return 0 if error_count == 0 else 1

    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

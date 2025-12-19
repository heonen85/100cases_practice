#!/usr/bin/env python3
"""
Garmin Connect FIT 파일 업로드 테스트
"""
import os
from garminconnect import Garmin
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv('/home/heone/100cases_practice/.env')

# Garmin 로그인 정보
email = os.getenv('GARMIN_EMAIL')
password = os.getenv('GARMIN_PASSWORD')

print(f"Garmin Connect 로그인 중... ({email})")

try:
    # Garmin Connect 로그인
    garmin = Garmin(email, password)
    garmin.login()

    print("✅ 로그인 성공!")

    # 업로드할 FIT 파일 경로
    fit_file = '/home/heone/100cases_practice/.playwright-mcp/2025-12-11.fit'

    print(f"\n파일 업로드 중: {fit_file}")

    # FIT 파일 업로드
    result = garmin.upload_activity(fit_file)

    print("✅ 업로드 성공!")
    print(f"결과: {result}")

except Exception as e:
    print(f"❌ 에러 발생: {type(e).__name__}")
    print(f"에러 내용: {str(e)}")

    # 중복 에러인지 확인
    if "duplicate" in str(e).lower() or "already" in str(e).lower():
        print("\n🔄 이미 업로드된 활동입니다 (중복)")

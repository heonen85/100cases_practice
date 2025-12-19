"""
Strava Access Token 갱신 스크립트
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
REFRESH_TOKEN = os.getenv('STRAVA_REFRESH_TOKEN')

def refresh_access_token():
    """Refresh Token으로 새로운 Access Token 발급"""

    print("="*60)
    print("Strava Access Token 갱신")
    print("="*60)

    url = "https://www.strava.com/oauth/token"
    payload = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': REFRESH_TOKEN,
        'grant_type': 'refresh_token'
    }

    print(f"\n요청 중...")
    print(f"Client ID: {CLIENT_ID}")
    print(f"Refresh Token: {REFRESH_TOKEN[:20]}...")

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()

        token_data = response.json()

        new_access_token = token_data['access_token']
        new_refresh_token = token_data['refresh_token']
        expires_at = token_data['expires_at']

        from datetime import datetime
        expiry_time = datetime.fromtimestamp(expires_at)

        print(f"\n✅ 토큰 갱신 성공!")
        print(f"\n새로운 Access Token:")
        print(f"{new_access_token}")
        print(f"\n새로운 Refresh Token:")
        print(f"{new_refresh_token}")
        print(f"\n만료 시간: {expiry_time}")

        # .env 파일 업데이트 안내
        print(f"\n{'='*60}")
        print(".env 파일을 아래 값으로 업데이트하세요:")
        print(f"{'='*60}")
        print(f"STRAVA_ACCESS_TOKEN={new_access_token}")
        print(f"STRAVA_REFRESH_TOKEN={new_refresh_token}")

        return token_data

    except requests.exceptions.RequestException as e:
        print(f"\n❌ 토큰 갱신 실패: {e}")
        if hasattr(e.response, 'text'):
            print(f"응답: {e.response.text}")
        return None

if __name__ == "__main__":
    refresh_access_token()

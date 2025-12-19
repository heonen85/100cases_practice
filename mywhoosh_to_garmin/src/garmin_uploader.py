"""
Garmin Connect 업로더
"""
from garminconnect import Garmin
from garth.exc import GarthHTTPError


class GarminUploader:
    """Garmin Connect에 활동 업로드"""

    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.garmin = None
        self._login()

    def _login(self):
        """Garmin Connect 로그인"""
        try:
            self.garmin = Garmin(self.email, self.password)
            self.garmin.login()
            print(f"  Garmin Connect 로그인 성공 ({self.email})")
        except Exception as e:
            print(f"  ❌ Garmin 로그인 실패: {e}")
            raise

    def upload(self, file_path):
        """
        FIT 파일 업로드

        Returns:
            dict: {
                'success': bool,
                'duplicate': bool,
                'error': str or None
            }
        """
        result = {
            'success': False,
            'duplicate': False,
            'error': None
        }

        try:
            self.garmin.upload_activity(file_path)
            result['success'] = True
            return result

        except GarthHTTPError as e:
            # HTTP 409 = 중복
            if '409' in str(e) or 'Conflict' in str(e):
                result['duplicate'] = True
                result['error'] = 'Duplicate activity'
            else:
                result['error'] = str(e)
            return result

        except Exception as e:
            result['error'] = str(e)
            return result

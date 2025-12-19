"""
다운로드/업로드 이력 관리
"""
import json
from pathlib import Path
from datetime import datetime


class HistoryManager:
    """활동 다운로드/업로드 이력 관리"""

    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        self.history_file = self.data_dir / "history.json"
        self.history = self._load_history()

    def _load_history(self):
        """이력 파일 로드"""
        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'uploaded': {},
            'downloaded': {}
        }

    def _save_history(self):
        """이력 파일 저장"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)

    def is_uploaded(self, file_name):
        """파일이 이미 업로드되었는지 확인"""
        return file_name in self.history['uploaded']

    def mark_uploaded(self, file_name):
        """파일을 업로드됨으로 표시"""
        self.history['uploaded'][file_name] = {
            'uploaded_at': datetime.now().isoformat(),
            'status': 'success'
        }
        self._save_history()

    def is_downloaded(self, file_name):
        """파일이 이미 다운로드되었는지 확인"""
        return file_name in self.history['downloaded']

    def mark_downloaded(self, file_name):
        """파일을 다운로드됨으로 표시"""
        self.history['downloaded'][file_name] = {
            'downloaded_at': datetime.now().isoformat()
        }
        self._save_history()

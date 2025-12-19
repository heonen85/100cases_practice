"""
JSON과 FIT 파일 자동 비교
"""
import sys
from compare_json_fit import analyze_json_file, analyze_fit_file, compare_data

# 파일 경로
json_path = "strava_data/2025-12-11_MyWhoosh_-_Sweetspot_#1_activity.json"
fit_path = "MyWhoosh_Sweetspot_1.fit"

print("="*60)
print("JSON (Strava API) vs FIT (원본) 비교")
print("="*60)

# 분석
json_data = analyze_json_file(json_path)
fit_data = analyze_fit_file(fit_path)

# 비교
if json_data and fit_data:
    compare_data(json_data, fit_data)

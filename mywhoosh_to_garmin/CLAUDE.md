# MyWhoosh to Garmin Connect - 프로젝트 문서

이 문서는 Claude Code와 함께 작업한 프로젝트의 상세 내역과 개발 이력을 담고 있습니다.

## 📋 목차

- [프로젝트 개요](#프로젝트-개요)
- [프로젝트 구조](#프로젝트-구조)
- [Strava API 연동](#strava-api-연동)
- [최근 작업 이력](#최근-작업-이력-2025-12-18)
- [스크립트 사용법](#스크립트-사용법)
- [데이터 비교 결과](#데이터-비교-결과)
- [문제 해결](#문제-해결)

---

## 프로젝트 개요

MyWhoosh 운동 데이터를 Garmin Connect로 자동 업로드하는 프로젝트입니다.

### 주요 기능
1. **MyWhoosh → Garmin 자동화**: 웹 스크래핑을 통한 FIT 파일 다운로드 및 Garmin 업로드
2. **Strava API 연동**: OAuth 2.0 기반 활동 데이터 다운로드 및 분석
3. **데이터 비교 도구**: JSON/FIT 파일 비교를 통한 데이터 무결성 검증
4. **포맷 변환**: JSON → GPX 변환 (Garmin 업로드 호환)

---

## 프로젝트 구조

```
mywhoosh_to_garmin/
├── README.md                          # 메인 프로젝트 문서
├── CLAUDE.md                          # 이 파일 - 개발 이력 및 상세 문서
├── .env                               # 환경 변수 (API 키, 로그인 정보)
├── .gitignore                         # Git 제외 파일
├── requirements.txt                   # Python 패키지 목록
├── MyWhoosh_Sweetspot_1.fit          # 비교용 FIT 파일
│
├── .github/workflows/                 # GitHub Actions 워크플로우
│   └── sync.yml                       # 자동 실행 스크립트
│
├── src/                               # 메인 자동화 파이프라인
│   ├── main.py                        # 통합 실행 스크립트
│   ├── mywhoosh_downloader.py         # MyWhoosh 웹 스크래핑
│   ├── garmin_uploader.py             # Garmin Connect 업로드
│   └── history_manager.py             # 중복 방지 이력 관리
│
├── scripts/                           # 유틸리티 스크립트
│   ├── strava/                        # Strava API 관련
│   │   ├── refresh_strava_token.py    # 토큰 갱신
│   │   ├── fetch_strava_activity.py   # 날짜별 활동 검색
│   │   ├── download_activity.py       # 활동 ID로 다운로드
│   │   └── strava_data_saver.py       # 데이터 저장 유틸리티
│   ├── comparison/                    # 데이터 비교 도구
│   │   ├── compare_fit_strava.py      # FIT vs Strava API 비교
│   │   ├── compare_json_fit.py        # JSON vs FIT 비교
│   │   └── run_comparison.py          # 비교 자동 실행
│   └── converter/                     # 포맷 변환 도구
│       └── json_to_gpx.py             # JSON → GPX 변환
│
├── tests/                             # 테스트 스크립트
│   └── test_upload.py                 # Garmin 업로드 테스트
│
├── docs/                              # 문서
│   ├── GITHUB_SETUP.md                # GitHub Actions 설정 가이드
│   └── BUGFIX_HISTORY.md              # 버그 수정 이력
│
├── data/                              # 데이터 저장
│   ├── history.json                   # 업로드 이력 (Git 추적)
│   └── strava_data/                   # Strava 다운로드 데이터
│       └── 2025-12-11_MyWhoosh_-_Sweetspot_#1_activity.json
│
├── downloads/                         # MyWhoosh 다운로드 FIT 파일 (.gitignore)
├── logs/                              # 실행 로그 (.gitignore)
└── screenshot/                        # 디버깅 스크린샷 (.gitignore)
```

---

## Strava API 연동

### OAuth 2.0 인증 흐름

Strava API는 OAuth 2.0을 사용하여 사용자 인증 및 권한 부여를 처리합니다.

#### 1단계: Authorization Code 발급

브라우저에서 아래 URL에 접속하여 권한을 승인합니다:

```
https://www.strava.com/oauth/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=read,activity:read_all,activity:write
```

**필수 권한 스코프:**
- `read`: 기본 프로필 읽기
- `activity:read_all`: 모든 활동 데이터 읽기
- `activity:write`: 활동 업로드/수정

승인 후 리다이렉트 URL에서 `code` 파라미터를 복사합니다:
```
http://localhost/?state=&code={AUTHORIZATION_CODE}&scope=...
```

⚠️ **주의사항:**
- Authorization Code는 **1회용**이며 **10분 후 만료**됩니다
- 이미 사용된 코드를 재사용하면 `{"message":"Authorization Error"}` 오류 발생

#### 2단계: Access Token 발급

```bash
curl -X POST https://www.strava.com/oauth/token \
  -d client_id={CLIENT_ID} \
  -d client_secret={CLIENT_SECRET} \
  -d code={AUTHORIZATION_CODE} \
  -d grant_type=authorization_code
```

**응답 예시:**
```json
{
  "token_type": "Bearer",
  "expires_at": 1734569316,
  "expires_in": 21600,
  "refresh_token": "062319a2e75fccc99e4289569892ca66635f788a",
  "access_token": "271e6c260b47060fe6c083c6d5534f8b2ffcf88d",
  "athlete": { ... }
}
```

#### 3단계: .env 파일 업데이트

```env
STRAVA_CLIENT_ID=166224
STRAVA_CLIENT_SECRET=c226abfbe0456b2b298fdaab450f2e7cd60968e9
STRAVA_ACCESS_TOKEN=271e6c260b47060fe6c083c6d5534f8b2ffcf88d
STRAVA_REFRESH_TOKEN=062319a2e75fccc99e4289569892ca66635f788a
```

### API 엔드포인트

**활동 목록 가져오기:**
```bash
curl -H "Authorization: Bearer {ACCESS_TOKEN}" \
  "https://www.strava.com/api/v3/athlete/activities?after={UNIX_TIMESTAMP}&per_page=30"
```

**활동 상세 정보:**
```bash
curl -H "Authorization: Bearer {ACCESS_TOKEN}" \
  "https://www.strava.com/api/v3/activities/{ACTIVITY_ID}"
```

**활동 스트림 데이터 (10종류):**
```bash
curl -H "Authorization: Bearer {ACCESS_TOKEN}" \
  "https://www.strava.com/api/v3/activities/{ACTIVITY_ID}/streams?keys=time,latlng,distance,altitude,velocity_smooth,heartrate,cadence,watts,temp,moving&key_by_type=true"
```

**스트림 데이터 타입:**
- `time`: 초 단위 경과 시간
- `latlng`: GPS 좌표 [위도, 경도]
- `distance`: 누적 거리 (미터)
- `altitude`: 고도 (미터)
- `velocity_smooth`: 속도 (m/s)
- `heartrate`: 심박수 (bpm)
- `cadence`: 케이던스 (rpm)
- `watts`: 파워 (W)
- `temp`: 온도 (°C)
- `moving`: 이동 중 여부 (boolean)

---

## 최근 작업 이력 (2025-12-18)

### 완료된 작업

#### 1. Strava OAuth 재인증 ✅
**문제:** 기존 Refresh Token이 무효화되어 API 호출 실패

**해결 과정:**
1. 수동 OAuth 2.0 흐름으로 새 Authorization Code 발급
2. 첫 번째 시도 실패 - Authorization Code 재사용 오류
3. 두 번째 시도 실패 - Client Secret 불일치 발견
   - 구 Client Secret: `b50f4c117036525c98b143699480135296e187dd`
   - 신 Client Secret: `c226abfbe0456b2b298fdaab450f2e7cd60968e9`
4. `.env` 파일 업데이트 후 OAuth 성공
5. 새 Access Token 및 Refresh Token 발급 완료

**결과:**
- Access Token: `271e6c260b47060fe6c083c6d5534f8b2ffcf88d`
- Refresh Token: `062319a2e75fccc99e4289569892ca66635f788a`
- 만료 시간: 6시간 (자동 갱신 필요)

#### 2. MyWhoosh 활동 다운로드 (2025-12-11) ✅
**목표:** 특정 날짜의 MyWhoosh 활동을 Strava API에서 JSON으로 다운로드

**작업 내역:**
1. `fetch_strava_activity.py` 실행으로 2025-12-11 활동 검색
2. 날짜 오류 수정: `2024-12-11` → `2025-12-11` (line 172)
3. 발견된 활동 3개:
   - MyWhoosh - Sweetspot #1 (ID: 16712292810) ⭐ **다운로드 대상**
   - MyWhoosh - Sweetspot #2 (ID: 16712334003)
   - MyWhoosh - Sweetspot #3 (ID: 16712377144)
4. `download_activity.py` 생성 - 활동 ID로 직접 다운로드
5. JSON 파일 저장: `strava_data/2025-12-11_MyWhoosh_-_Sweetspot_#1_activity.json`

**결과:**
- 파일 크기: 579.3 KB
- 데이터 포인트: 3,009개
- 스트림 타입: 10종류 (time, watts, heartrate, cadence, distance 등)

#### 3. JSON vs FIT 비교 분석 ✅
**목표:** Strava API JSON 데이터와 원본 FIT 파일의 무결성 검증

**비교 대상:**
- JSON: `strava_data/2025-12-11_MyWhoosh_-_Sweetspot_#1_activity.json` (579.3 KB)
- FIT: `MyWhoosh_Sweetspot_1.fit` (74.4 KB)

**비교 스크립트:**
- `scripts/comparison/compare_json_fit.py`: 필드별 상세 비교
- `scripts/comparison/run_comparison.py`: 자동 비교 실행

**비교 결과:**

| 항목 | JSON (Strava API) | FIT (원본) | 비고 |
|------|-------------------|------------|------|
| 파일 크기 | 579.3 KB | 74.4 KB | FIT가 **7.8배 효율적** |
| 데이터 포인트 | 3,009개 | 3,009개 | ✅ 동일 |
| 파워 데이터 | ✅ 있음 (watts) | ✅ 있음 (power) | ✅ 보존됨 |
| 심박수 | ✅ 있음 | ✅ 있음 | ✅ 보존됨 |
| 케이던스 | ✅ 있음 | ✅ 있음 | ✅ 보존됨 |
| GPS 좌표 | ❌ 없음 | ❌ 없음 | 실내 라이딩 (정상) |
| 온도 | ✅ 있음 | ❌ 없음 | JSON에만 존재 |

**결론:**
- ✅ **모든 핵심 데이터 보존 확인** (파워, 심박수, 케이던스, 거리, 시간)
- ✅ FIT 파일이 바이너리 압축으로 7.8배 더 효율적
- ✅ Strava API는 추가 메타데이터 제공 (온도, 이동 여부 등)
- ⚠️ Garmin Connect는 JSON 업로드 **불가** (FIT/TCX/GPX만 지원)

#### 4. 프로젝트 구조 정리 ✅
**목표:** 산출물을 카테고리별 폴더로 정리하고 문서화

**폴더 구조 변경:**
```bash
# 생성된 폴더
scripts/strava/       # Strava API 스크립트 4개
scripts/comparison/   # 비교 도구 3개
scripts/converter/    # 변환 도구 1개
docs/                 # 문서 2개
tests/                # 테스트 1개

# 최상위 폴더 정리
- README.md (유지)
- CLAUDE.md (신규 생성) ⭐
- .env, .gitignore, requirements.txt (유지)
```

**파일 이동 이력:**
- `refresh_strava_token.py` → `scripts/strava/`
- `fetch_strava_activity.py` → `scripts/strava/`
- `download_activity.py` → `scripts/strava/`
- `strava_data_saver.py` → `scripts/strava/`
- `compare_fit_strava.py` → `scripts/comparison/`
- `compare_json_fit.py` → `scripts/comparison/`
- `run_comparison.py` → `scripts/comparison/`
- `json_to_gpx.py` → `scripts/converter/`
- `test_upload.py` → `tests/`
- `GITHUB_SETUP.md` → `docs/`
- `BUGFIX_HISTORY.md` → `docs/`

---

## 스크립트 사용법

### 1. Strava API 스크립트

#### 토큰 갱신
```bash
cd scripts/strava
python refresh_strava_token.py
```

#### 날짜별 활동 검색
```bash
cd scripts/strava
python fetch_strava_activity.py
# target_date 변수 수정 필요 (line 172)
```

#### 활동 ID로 다운로드
```bash
cd scripts/strava
python download_activity.py
# activity_id 변수 수정 필요 (line 47)
```

### 2. 비교 도구

#### JSON vs FIT 자동 비교
```bash
cd scripts/comparison
python run_comparison.py
# 파일 경로 하드코딩 (line 123-124)
```

#### 상세 비교 (수동)
```bash
cd scripts/comparison
python compare_json_fit.py
```

### 3. 변환 도구

#### JSON → GPX 변환
```bash
cd scripts/converter
python json_to_gpx.py
# 입력/출력 파일 경로 수정 필요
```

---

## 데이터 비교 결과

### 파일 크기 비교

```
JSON: 579.3 KB (텍스트 기반, 사람이 읽을 수 있음)
FIT:   74.4 KB (바이너리 압축, 7.8배 효율적)
```

### 데이터 포인트 비교

```
총 데이터 포인트: 3,009개 (양쪽 동일)
샘플링 레이트: 약 1초당 1개
활동 시간: 약 50분
```

### 스트림 데이터 매칭

| Strava JSON 필드 | FIT 필드 | 매칭 여부 |
|------------------|----------|-----------|
| `streams.time` | `timestamp` | ✅ 일치 |
| `streams.watts` | `power` | ✅ 일치 |
| `streams.heartrate` | `heart_rate` | ✅ 일치 |
| `streams.cadence` | `cadence` | ✅ 일치 |
| `streams.distance` | `distance` | ✅ 일치 |
| `streams.velocity_smooth` | `speed` | ✅ 일치 |
| `streams.temp` | - | ⚠️ FIT에 없음 |
| `streams.moving` | - | ⚠️ FIT에 없음 |

### 메타데이터 비교

| 항목 | Strava JSON | FIT |
|------|-------------|-----|
| 활동 이름 | "MyWhoosh - Sweetspot #1" | ✅ 있음 |
| 활동 타입 | "VirtualRide" | ✅ 있음 |
| 시작 시간 | ISO 8601 | ✅ 있음 |
| 총 시간 | 3,008초 | ✅ 일치 |
| 이동 시간 | 2,946초 | ✅ 있음 |
| 평균 파워 | 148 W | ✅ 일치 |
| 최대 파워 | 298 W | ✅ 일치 |
| 평균 심박수 | 121 bpm | ✅ 일치 |
| 총 거리 | 24.8 km | ✅ 일치 |
| 총 상승 고도 | 28 m | ✅ 일치 |

---

## 문제 해결

### Strava API 관련

#### 1. Authorization Error
**증상:** `{"message":"Authorization Error","errors":[{"resource":"Application","field":"","code":"invalid"}]}`

**원인:**
- Authorization Code 재사용 (1회용 코드)
- Client Secret 불일치
- 만료된 Authorization Code (10분 후 만료)

**해결 방법:**
1. Strava API 설정 페이지에서 Client Secret 확인
2. 새 Authorization Code 발급 (OAuth URL 재접속)
3. `.env` 파일의 `STRAVA_CLIENT_SECRET` 업데이트
4. 즉시 curl로 토큰 발급 (10분 이내)

#### 2. Access Token 만료
**증상:** API 호출 시 `401 Unauthorized`

**해결 방법:**
```bash
cd scripts/strava
python refresh_strava_token.py
```

#### 3. 날짜 검색 결과 없음
**증상:** `fetch_strava_activity.py` 실행 시 활동이 없다고 나옴

**해결 방법:**
- `target_date` 변수의 연도 확인 (2024 vs 2025)
- Unix timestamp 변환 확인
- Strava 웹사이트에서 해당 날짜 활동 존재 여부 확인

### 데이터 변환 관련

#### JSON을 Garmin에 업로드할 수 없는 이유
Garmin Connect는 다음 형식만 지원합니다:
- ✅ FIT (Flexible and Interoperable Data Transfer)
- ✅ TCX (Training Center XML)
- ✅ GPX (GPS Exchange Format)
- ❌ JSON (지원 안 함)

**해결 방법:**
1. `scripts/converter/json_to_gpx.py` 사용하여 GPX로 변환
2. Garmin Connect 웹사이트에서 수동 업로드
3. 또는 원본 FIT 파일 사용 (가장 권장)

### GitHub Actions 관련

자세한 내용은 `docs/GITHUB_SETUP.md` 참고

---

## 향후 계획

### 잠재적 개선 사항
1. **Strava → Garmin 자동 동기화**: Strava 활동을 Garmin으로 자동 전송
2. **데이터 분석 대시보드**: 파워 존, 심박수 존 분석
3. **활동 비교 리포트**: 동일 코스의 다른 날짜 활동 비교
4. **자동 토큰 갱신**: Access Token 만료 시 자동 Refresh

---

## 기술 스택

### 언어 및 프레임워크
- Python 3.12+
- Playwright (웹 스크래핑)
- python-garminconnect (Garmin API)
- python-dotenv (환경 변수)
- fitparse (FIT 파일 파싱)
- requests (HTTP 클라이언트)

### 외부 API
- Strava API v3 (OAuth 2.0)
- Garmin Connect API (OAuth 1.0a)
- MyWhoosh (공식 API 없음, 웹 스크래핑)

### 인프라
- GitHub Actions (CI/CD)
- Git (버전 관리, 이력 영구 보존)

---

## 참고 자료

- [Strava API Documentation](https://developers.strava.com/docs/reference/)
- [python-garminconnect GitHub](https://github.com/cyberjunky/python-garminconnect)
- [FIT SDK](https://developer.garmin.com/fit/protocol/)
- [Playwright Python](https://playwright.dev/python/)

---

**문서 작성일:** 2025-12-18
**마지막 업데이트:** 2025-12-18
**작성자:** Claude Code (Sonnet 4.5)

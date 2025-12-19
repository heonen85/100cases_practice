# 100 Cases Practice - 프로젝트 가이드

## 📋 프로젝트 개요

이 저장소는 Playwright MCP를 활용한 실습 프로젝트입니다. 주요 프로젝트인 **MyWhoosh to Garmin Connect 자동화**와 **Strava API 연동**을 포함하고 있습니다.

### 프로젝트 목적
- MyWhoosh 운동 데이터를 Garmin Connect로 자동 동기화
- Strava API를 통한 활동 데이터 백업 및 분석
- GitHub Actions를 통한 모바일 실행 지원
- 웹 스크래핑 및 API 연동 실습

---

## 📁 프로젝트 구조

```
100cases_practice/
├── README.md                    # 저장소 개요
├── CLAUDE.md                    # 이 파일 - Claude Code 작업 가이드
│
├── .claude/                     # Claude Code 설정
├── .playwright-mcp/             # Playwright MCP 관련 파일
│   └── screenshot/              # MCP 스크린샷 (YYMMDD_hhmm_*.png 형식)
│
└── mywhoosh_to_garmin/          # 메인 프로젝트 ⭐
    ├── README.md                # 프로젝트 상세 문서
    ├── requirements.txt         # Python 패키지 의존성
    ├── .env                     # 환경 변수 (민감 정보, Git 제외)
    ├── .gitignore               # Git 제외 파일 목록
    ├── MyWhoosh_Sweetspot_1.fit # 샘플 FIT 파일
    │
    ├── src/                     # 메인 소스 코드 (자동화 파이프라인)
    │   ├── main.py              # 전체 프로세스 통합
    │   ├── mywhoosh_downloader.py    # MyWhoosh 웹 스크래핑
    │   ├── garmin_uploader.py        # Garmin Connect 업로드
    │   └── history_manager.py        # 중복 방지 이력 관리
    │
    ├── scripts/                 # 유틸리티 스크립트 모음
    │   ├── strava/              # Strava API 관련
    │   │   ├── refresh_strava_token.py    # OAuth 토큰 갱신
    │   │   ├── fetch_strava_activity.py   # 날짜별 활동 조회
    │   │   ├── download_activity.py       # 특정 활동 다운로드
    │   │   └── strava_data_saver.py       # 다양한 형식으로 저장
    │   ├── comparison/          # 데이터 비교 분석
    │   │   ├── compare_fit_strava.py      # FIT vs Strava API 비교
    │   │   ├── compare_json_fit.py        # JSON vs FIT 비교
    │   │   └── run_comparison.py          # 자동 비교 실행
    │   └── converter/           # 파일 형식 변환
    │       └── json_to_gpx.py             # JSON을 GPX로 변환
    │
    ├── tests/                   # 테스트 스크립트
    │   └── test_upload.py       # Garmin 업로드 테스트
    │
    ├── docs/                    # 문서
    │   ├── GITHUB_SETUP.md      # GitHub Actions 설정 가이드
    │   └── BUGFIX_HISTORY.md    # 버그 수정 이력 (필독!)
    │
    ├── data/                    # 데이터 및 이력
    │   ├── history.json         # 다운로드/업로드 이력 (Git 추적!)
    │   └── strava_data/         # Strava API 백업 데이터
    │       └── 2025-12-11_MyWhoosh_-_Sweetspot_#1_activity.json
    │
    ├── downloads/               # MyWhoosh FIT 파일 (Git 제외)
    ├── logs/                    # 실행 로그 (Git 제외)
    ├── screenshot/              # 디버깅 스크린샷 (Git 제외)
    └── .venv/                   # Python 가상환경
```

---

## 🎯 주요 기능

### 1. MyWhoosh 데이터 다운로드 (`src/mywhoosh_downloader.py`)
- **Playwright 웹 스크래핑** 사용 (공식 API 없음)
- 최근 N일 활동 다운로드 (기본 30일)
- FIT 파일 형식으로 저장 (원본 데이터 보존)
- 자동 정책 동의 처리
- reCAPTCHA 자동 검증 (3단계 전략)

### 2. Garmin Connect 업로드 (`src/garmin_uploader.py`)
- `python-garminconnect` 라이브러리 사용
- OAuth 인증 처리
- 중복 자동 감지 (HTTP 409)
- 에러 핸들링 및 로깅

### 3. Strava API 연동 (`scripts/strava/`)
- **OAuth 2.0 인증**: Access Token 및 Refresh Token 관리
- **활동 조회**: 날짜별 필터링 및 검색
- **데이터 다운로드**: JSON, GPX, CSV 형식 지원
- **자동 토큰 갱신**: Refresh Token으로 Access Token 갱신

**주요 스크립트**:
- `refresh_strava_token.py`: 만료된 토큰 갱신
- `fetch_strava_activity.py`: 날짜별 활동 조회
- `download_activity.py`: 특정 활동 ID로 JSON 다운로드
- `strava_data_saver.py`: 다양한 형식(JSON/GPX/CSV)으로 저장

### 4. 데이터 비교 분석 (`scripts/comparison/`)
- **FIT vs JSON 비교**: 데이터 손실 여부 확인
- **필드 매핑 분석**: 어떤 데이터가 보존되는지 확인
- **통계 비교**: 거리, 시간, 속도 등 정확도 검증

**분석 결과 예시**:
```
데이터 포인트: 3,009 (양쪽 동일) ✅
파일 크기: FIT 74KB vs JSON 579KB (7.8배 차이)
필드 보존율: 80%
핵심 데이터: 파워, 심박수, 케이던스 모두 보존 ✅
```

### 5. 파일 형식 변환 (`scripts/converter/`)
- **JSON → GPX**: Garmin/Strava에 업로드 가능한 GPX 형식으로 변환
- GPS 좌표, 심박수, 파워 데이터 포함
- Garmin TrackPointExtension 지원

### 6. 이력 관리 (`src/history_manager.py`)
- **3중 중복 방지 메커니즘**:
  1. 로컬 파일 존재 체크
  2. `history.json` 기록 확인
  3. Garmin 서버 중복 감지
- Git 저장소에 이력 커밋 (GitHub Actions 영속성)

### 7. GitHub Actions 워크플로우
- 모바일에서 실행 가능 (핸드폰으로 "Run workflow" 클릭)
- 자동 스케줄링 지원
- 이력 파일 자동 커밋 (`[skip ci]`로 무한 루프 방지)
- Artifacts로 로그 및 스크린샷 저장

---

## 🛠️ 기술 스택

### Backend
- **Python 3.12+**
- **Playwright**: 웹 스크래핑 (Chromium headless)
- **python-garminconnect**: Garmin API 클라이언트
- **python-dotenv**: 환경 변수 관리
- **requests**: Strava API 호출
- **fitparse**: FIT 파일 분석 (선택적)

### Infrastructure
- **GitHub Actions**: CI/CD 및 클라우드 실행
- **Git**: 이력 관리 영속성

### MCP Servers
- **Playwright MCP**: 브라우저 자동화
- **Codex MCP**: 코드 실행 도구

---

## 🚀 로컬 개발 환경 설정

### 1. Python 가상환경 설정
```bash
cd mywhoosh_to_garmin/

# uv 사용 (추천)
uv venv
source .venv/bin/activate  # Linux/Mac
# or .venv\Scripts\activate  # Windows

# 패키지 설치
uv pip install -r requirements.txt

# Playwright 브라우저 설치
playwright install chromium
```

### 2. 환경 변수 설정
`.env` 파일 생성:
```env
# MyWhoosh Event 로그인 정보
MYWHOOSH_EMAIL=your_email@example.com
MYWHOOSH_PASSWORD=your_password

# Garmin Connect 로그인 정보
GARMIN_EMAIL=your_email@example.com
GARMIN_PASSWORD=your_password

# Strava API 정보
STRAVA_CLIENT_ID=your_client_id
STRAVA_CLIENT_SECRET=your_client_secret
STRAVA_ACCESS_TOKEN=your_access_token
STRAVA_REFRESH_TOKEN=your_refresh_token
```

### 3. 실행

#### 메인 자동화 파이프라인
```bash
# 전체 동기화 (MyWhoosh → Garmin)
python src/main.py
```

#### Strava API 스크립트
```bash
# 토큰 갱신
python scripts/strava/refresh_strava_token.py

# 특정 날짜 활동 조회
python scripts/strava/fetch_strava_activity.py

# 특정 활동 다운로드 (ID 지정)
python scripts/strava/download_activity.py
```

#### 데이터 비교
```bash
# JSON vs FIT 비교
python scripts/comparison/run_comparison.py
```

#### 파일 변환
```bash
# JSON을 GPX로 변환
python scripts/converter/json_to_gpx.py
```

---

## 🔄 최근 작업 이력

### ✅ 2025-12-19 작업

1. **Playwright MCP 스크린샷 관리 시스템 구축**
   - `.playwright-mcp/screenshot/` 폴더 생성
   - 기존 PNG 파일 5개 정리 및 이동
   - 타임스탬프 접두어 적용: `YYMMDD_hhmm_` 형식
   - CLAUDE.md에 스크린샷 규칙 문서화

**정리된 파일**:
- `251213_1256_naver_screenshot.png` (814 KB)
- `251213_1326_garmin-connect-homepage.png` (766 KB)
- `251213_1704_mywhoosh-recaptcha-challenge.png` (344 KB)
- `251213_1706_mywhoosh-logged-in.png` (174 KB)
- `251213_1709_mywhoosh-activities.png` (235 KB)

### ✅ 2025-12-18 작업

1. **Strava OAuth 재인증 성공**
   - Client Secret 불일치 문제 발견 및 수정
   - 새로운 Access Token 및 Refresh Token 발급
   - `.env` 파일 자동 업데이트

2. **2025년 12월 11일 MyWhoosh 활동 데이터 다운로드**
   - 활동명: MyWhoosh - Sweetspot #1
   - 타입: VirtualRide
   - 거리: 21.22 km, 시간: 50.1분
   - JSON 형식으로 저장 (579 KB)
   - 포함 데이터: 파워, 심박수, 케이던스, GPS 등 10가지 스트림
   - 총 3,009 데이터 포인트

3. **JSON vs FIT 비교 분석 완료**
   - 데이터 포인트 수: 완전 일치 (3,009)
   - 필드 보존율: 80%
   - 핵심 데이터 완벽 보존 (파워, 심박수, 케이던스)
   - 파일 크기: FIT가 7.8배 더 효율적

4. **프로젝트 구조 재정리**
   - `scripts/` 폴더 생성: strava/, comparison/, converter/ 카테고리화
   - `docs/` 폴더 생성: 문서 통합 관리
   - `tests/` 폴더 생성: 테스트 코드 분리
   - 최상위 폴더 정리: README.md, CLAUDE.md만 유지

### 📊 비교 분석 결과

**FIT 파일**:
- 크기: 74.4 KB (이진 압축)
- 포인트: 3,009개
- 필드: 11개 (enhanced_altitude, enhanced_speed 포함)

**JSON 파일 (Strava API)**:
- 크기: 579.3 KB (텍스트)
- 포인트: 3,009개
- 스트림: 10개 (grade_smooth, moving 추가)

**결론**:
- ✅ 데이터 완전성: 동일
- ✅ 핵심 지표 보존: 파워, 심박수, 케이던스 모두 포함
- 📦 저장 효율: FIT가 7.8배 우수
- 💡 **추천**: 백업은 JSON, 업로드는 FIT

---

## 🐛 알려진 이슈 및 해결 방법

**반드시 `docs/BUGFIX_HISTORY.md`를 참고하세요!**

### 주요 해결된 문제들

1. **로그인 셀렉터 타임아웃** → 구체적인 셀렉터 + 타임아웃 증가
2. **Submit 버튼 비활성화** → "Accept All" 정책 동의 추가
3. **reCAPTCHA 체크박스 미클릭** → 3단계 클릭 전략 (`force=True`, 좌표 클릭)
4. **GitHub Actions 중복 다운로드** → `history.json` Git 커밋으로 영속성 확보
5. **스크린샷 파일 흩어짐** → `screenshot/` 폴더로 통합
6. **Strava Client Secret 불일치** → API 설정 페이지에서 최신 값 확인
7. **Authorization Code 1회용 문제** → 10분 이내 즉시 사용

### Strava API 관련 주의사항

1. **OAuth 토큰 관리**:
   - Access Token: 6시간마다 만료
   - Refresh Token: 영구적이지만 재사용 시 무효화
   - 토큰 갱신 시 **새 Refresh Token도 함께 업데이트** 필수

2. **Authorization Code**:
   - 1회용 코드 (사용 후 즉시 무효화)
   - 10분 내에 사용해야 함
   - 재사용 불가 → 에러 발생 시 새 코드 발급 필요

3. **Client Secret 변경**:
   - Strava API 설정에서 Secret 재생성 시 모든 토큰 무효화
   - `.env` 파일과 API 설정의 Secret이 일치해야 함

### 디버깅 팁
- **스크린샷 확인**: `screenshot/` 폴더 또는 GitHub Actions Artifacts
- **로그 확인**: `logs/` 폴더 또는 GitHub Actions 로그
- **이력 확인**: `data/history.json` 내용 검토
- **Strava 토큰**: `refresh_strava_token.py` 실행하여 갱신

---

## ⚠️ 주의사항

### 보안
- **절대 커밋 금지**: `.env` 파일, 실제 비밀번호
- **Private 저장소 사용 권장**: 개인 운동 데이터 보호
- **GitHub Secrets 사용**: Actions 실행 시 환경 변수
- **Strava Client Secret 노출 방지**: 공개 저장소에 올리지 말 것

### Git 관리
- `data/history.json`은 **의도적으로 Git에 포함**됨 (중복 방지용)
- `data/strava_data/`는 백업 데이터 저장소 (필요시 Git 추가)
- `downloads/`, `logs/`, `screenshot/`는 `.gitignore`에 포함
- `.venv/`는 Git에 포함하지 않음

### 코드 수정 시
- `src/mywhoosh_downloader.py`: 셀렉터 변경 시 신중하게
- `src/history_manager.py`: 이력 관리 로직 수정 시 백업 필수
- `scripts/strava/`: API 호출 전 토큰 유효성 확인
- 워크플로우 수정 시 `[skip ci]` 주의

---

## 📚 추가 문서

- **[README.md](mywhoosh_to_garmin/README.md)**: 프로젝트 전체 설명
- **[docs/GITHUB_SETUP.md](mywhoosh_to_garmin/docs/GITHUB_SETUP.md)**: GitHub Actions 설정 가이드
- **[docs/BUGFIX_HISTORY.md](mywhoosh_to_garmin/docs/BUGFIX_HISTORY.md)**: 문제 해결 이력 (필독!)

---

## 🤖 Claude Code 작업 시 참고사항

### Playwright MCP 스크린샷 규칙 ⭐
**IMPORTANT**: Playwright MCP를 통한 모든 스크린샷 캡처 시 반드시 다음 규칙을 따를 것!

1. **저장 경로**: `.playwright-mcp/screenshot/` (고정)
2. **파일명 형식**: `YYMMDD_hhmm_설명.png`
   - `YY`: 연도 (2자리, 예: 25)
   - `MM`: 월 (2자리, 예: 12)
   - `DD`: 일 (2자리, 예: 19)
   - `hh`: 시간 (24시간 형식, 2자리, 예: 14)
   - `mm`: 분 (2자리, 예: 30)
   - `설명`: 스크린샷 내용 설명 (영문, 하이픈 구분)

3. **예시**:
   ```
   .playwright-mcp/screenshot/251219_1430_login-page.png
   .playwright-mcp/screenshot/251219_1432_recaptcha-challenge.png
   .playwright-mcp/screenshot/251219_1435_activity-list.png
   ```

4. **Python 코드 예시**:
   ```python
   from datetime import datetime

   # 현재 시간 기반 파일명 생성
   now = datetime.now()
   filename = f".playwright-mcp/screenshot/{now.strftime('%y%m%d_%H%M')}_description.png"
   page.screenshot(path=filename)
   ```

### 토큰 사용량 모니터링 및 경고 ⚠️
**CRITICAL**: 대화 중 토큰 사용량을 지속적으로 모니터링하고, 부족 시 사용자에게 미리 경고할 것!

#### 경고 기준
- **2회 이하의 파일 읽기/수정 작업만 가능한 상황** 시 즉시 경고 발생
- 기준: 남은 토큰이 **약 20,000 토큰 이하**일 때 (파일 1회 작업 ≈ 10,000 토큰)

#### 경고 메시지 형식
```
⚠️ 토큰 부족 경고!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
현재 남은 토큰: XX,XXX / 200,000 (XX%)
예상 가능 작업: 파일 읽기/수정 약 X회

💡 권장 사항:
1. 현재 대화 정리 필요 (새 대화 시작 권장)
2. 중요한 작업 먼저 완료
3. 복잡한 파일 작업은 다음 세션으로 연기
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### 모니터링 시점
1. **파일 읽기 전**: Read 도구 사용 전 토큰 체크
2. **파일 수정 전**: Edit/Write 도구 사용 전 토큰 체크
3. **대형 작업 시작 전**: Task 도구로 에이전트 실행 전 체크
4. **사용자 질문 시**: 복잡한 질문 답변 전 체크

#### 토큰 추정 가이드
- 평균 파일 읽기: **5,000~15,000 토큰** (파일 크기에 따라)
- 파일 수정: **3,000~8,000 토큰**
- 복잡한 응답: **2,000~5,000 토큰**
- Task 에이전트 실행: **10,000~30,000 토큰**

**IMPORTANT**: 경고 발생 시 사용자에게 명확히 알리고, 작업 우선순위를 조정하거나 새 대화 시작을 권장할 것!

### 파일 수정 전 확인사항
1. `docs/BUGFIX_HISTORY.md` 먼저 읽어보기 (과거 이슈 반복 방지)
2. 웹 스크래핑 코드 수정 시 스크린샷 추가
3. 셀렉터 변경 시 여러 후보 유지 (fallback 전략)
4. Strava API 호출 시 토큰 만료 확인

### 테스트 순서
1. 로컬 테스트: `python src/main.py`
2. Strava API 테스트: `python scripts/strava/fetch_strava_activity.py`
3. 비교 분석: `python scripts/comparison/run_comparison.py`
4. GitHub Actions 테스트: 워크플로우 실행
5. 스크린샷 확인: Artifacts 다운로드

### 디버깅 코드 추가 시
```python
# 스크린샷 캡처
screenshot_path = self.screenshot_dir / "debug_step.png"
page.screenshot(path=str(screenshot_path))

# 상태 로깅
print(f"  디버그: {변수명} = {값}")

# 입력 값 검증
value = element.input_value()
print(f"  입력 확인: {value}")

# API 응답 확인
print(f"  API 응답: {response.status_code}")
print(f"  데이터: {response.json()}")
```

---

## 🎓 학습 포인트

이 프로젝트를 통해 배울 수 있는 것들:
- ✅ Playwright를 이용한 웹 스크래핑
- ✅ reCAPTCHA 자동 처리 전략
- ✅ GitHub Actions CI/CD 구축
- ✅ Python 비동기 프로그래밍
- ✅ API 클라이언트 라이브러리 사용 (Garmin, Strava)
- ✅ OAuth 2.0 인증 흐름 이해
- ✅ 이력 관리 및 중복 방지 메커니즘
- ✅ 클라우드 환경 디버깅 기법
- ✅ FIT, JSON, GPX 등 다양한 데이터 형식 다루기
- ✅ 데이터 비교 및 분석 기법

---

## 🔮 향후 개선 계획

- [ ] MyWhoosh → Strava 직접 업로드 자동화
- [ ] Garmin ↔ Strava 자동 동기화 설정 가이드
- [ ] JSON → FIT 역변환 기능 (고급)
- [ ] 데이터 시각화 대시보드 (Matplotlib/Plotly)
- [ ] 텔레그램 알림 연동
- [ ] 다중 플랫폼 동시 업로드 (Garmin + Strava + 기타)

---

**마지막 업데이트**: 2025-12-19
**프로젝트 상태**: ✅ 안정화 완료, 운영 중
**최근 추가**:
- Playwright MCP 스크린샷 관리 시스템 구축 완료
- 토큰 사용량 모니터링 및 자동 경고 시스템 추가

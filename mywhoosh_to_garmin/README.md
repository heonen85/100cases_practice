# MyWhoosh to Garmin Connect 자동화

MyWhoosh 운동 데이터를 Garmin Connect로 자동 업로드하는 프로젝트입니다.

## 📱 주요 특징

- **모바일 실행 가능**: GitHub Actions를 통해 핸드폰에서 실행
- **FIT 파일 다운로드**: MyWhoosh에서 FIT 형식으로 다운로드 (원본 데이터 보존)
- **자동 업로드**: Garmin Connect에 자동 업로드
- **중복 방지**: 3중 중복 방지 메커니즘으로 동일 활동 재업로드 차단
- **완전 자동화**: 로그인부터 업로드까지 전 과정 자동화

## 🔄 작동 방식

### MyWhoosh 데이터 다운로드
- **방식**: 웹 스크래핑 (Playwright)
- **이유**: MyWhoosh는 공식 API를 제공하지 않음
- **과정**:
  1. https://event.mywhoosh.com/ 로그인
  2. 정책 동의 (Accept All)
  3. reCAPTCHA 검증
  4. Activities 페이지에서 활동 목록 확인
  5. FIT 파일 다운로드 (파일명: YYYY-MM-DD.fit)

### Garmin Connect 업로드
- **방식**: python-garminconnect API 라이브러리
- **과정**:
  1. Garmin OAuth 인증
  2. FIT 파일 업로드
  3. 중복 자동 감지 (HTTP 409 Conflict)

## 🛡️ 중복 방지 메커니즘

GitHub Actions는 매번 새로운 컨테이너에서 실행되므로, 이력 관리를 위해 특별한 방법을 사용합니다.

### 문제점
```
실행 1: downloads/ 폴더 비어있음 → 30일치 전부 다운로드
실행 2: downloads/ 폴더 비어있음 → 또 30일치 전부 다운로드 (중복!)
```

### 해결 방법
`data/history.json` 파일을 Git 저장소에 커밋하여 영구 보존

**동작 방식:**
1. 스크립트 실행 시 `data/history.json` 읽기
2. 이미 다운로드/업로드한 활동은 건너뛰기
3. 새로운 활동만 처리
4. `data/history.json` 업데이트
5. **자동 커밋 및 푸시** (GitHub Actions)

**3중 중복 방지:**
1. **로컬 파일 존재 체크**: `downloads/2025-12-14.fit` 이미 있으면 건너뜀
2. **이력 관리자**: `history.json`에 기록된 활동 건너뜀
3. **Garmin 서버**: HTTP 409 Conflict로 중복 업로드 거부

## 🛠️ 기술 스택

- **Python 3.12+**
- **Playwright**: MyWhoosh 웹 스크래핑
- **python-garminconnect**: Garmin API 클라이언트
- **python-dotenv**: 환경 변수 관리
- **GitHub Actions**: 클라우드 실행 환경

## 📁 프로젝트 구조

```
mywhoosh_to_garmin/
├── README.md                      # 프로젝트 문서
├── GITHUB_SETUP.md                # GitHub Actions 설정 가이드
├── BUGFIX_HISTORY.md              # 버그 수정 이력
├── .env                           # 환경 변수 (로컬 테스트용)
├── .gitignore                     # Git 제외 파일
├── requirements.txt               # Python 패키지 목록
├── .github/workflows/sync.yml     # GitHub Actions 워크플로우
├── src/
│   ├── mywhoosh_downloader.py     # MyWhoosh 다운로더
│   ├── garmin_uploader.py         # Garmin 업로더
│   ├── history_manager.py         # 이력 관리
│   └── main.py                    # 메인 스크립트
├── data/
│   └── history.json               # 다운로드/업로드 이력 (Git 저장)
├── downloads/                     # 다운로드된 FIT 파일
├── logs/                          # 실행 로그
└── screenshot/                    # 디버깅 스크린샷
```

## ⚙️ 환경 설정

### 1. .env 파일 (로컬 테스트용)

```env
# MyWhoosh Event 로그인 정보
MYWHOOSH_EMAIL=your_email@example.com
MYWHOOSH_PASSWORD=your_password

# Garmin Connect 로그인 정보
GARMIN_EMAIL=your_email@example.com
GARMIN_PASSWORD=your_password
```

### 2. Python 패키지 설치 (로컬 실행 시)

```bash
# 가상환경 생성
uv venv

# 패키지 설치
uv pip install garminconnect python-dotenv playwright

# Playwright 브라우저 설치
playwright install chromium
```

## 📱 사용법

### ⭐ 모바일에서 실행 (GitHub Actions - 추천)

**가장 쉽고 편리한 방법입니다!**

1. GitHub 저장소 생성 및 코드 업로드
2. GitHub Secrets 설정 (로그인 정보)
3. 모바일에서 GitHub Actions 탭 → "Run workflow" 버튼 클릭

자세한 설정 방법은 **[GITHUB_SETUP.md](GITHUB_SETUP.md)** 참고

### 💻 PC에서 로컬 실행

#### 전체 동기화 실행
```bash
python src/main.py
```

#### Garmin 업로드 테스트만
```bash
python test_upload.py
```

## ✅ 구현 완료

### 1. MyWhoosh 다운로더 (`src/mywhoosh_downloader.py`)
- Playwright로 웹 스크래핑
- 최근 N일 활동 다운로드
- 정책 동의 자동 처리 (Accept All)
- reCAPTCHA 자동 검증 (3단계 전략)
- 날짜별 필터링

### 2. Garmin 업로더 (`src/garmin_uploader.py`)
- python-garminconnect 사용
- 중복 자동 감지
- 에러 핸들링

### 3. 이력 관리 (`src/history_manager.py`)
- JSON 파일로 이력 관리 (`data/history.json`)
- Git 저장소에 이력 파일 커밋 (GitHub Actions에서 영구 보존)
- 중복 다운로드/업로드 방지

### 4. 메인 스크립트 (`src/main.py`)
- 전체 프로세스 통합
- 로그 출력

### 5. GitHub Actions 워크플로우
- 모바일에서 실행 가능
- 자동 스케줄링 지원
- 로그 및 파일 Artifacts 저장
- 이력 파일 자동 커밋 (중복 다운로드 방지)
- 디버깅 스크린샷 업로드

## 🎯 활동 필터링

기본적으로 **최근 30일 이내**의 활동을 다운로드합니다.

```python
# src/mywhoosh_downloader.py
downloader.download_recent_activities(days=30)
```

날짜 범위를 변경하려면 `days` 값을 조정하세요.

## 💰 비용

**완전 무료**: GitHub Actions는 Public/Private 저장소 모두 월 2,000분 무료
- 이 워크플로우는 약 2-5분 소요
- 매일 실행해도 월 150분 정도만 사용 (무료 범위 내)

## 🔒 보안

- **Private 저장소 사용**: 코드에 개인정보가 포함되지 않도록
- **GitHub Secrets**: 비밀번호가 로그에 노출되지 않음
- **토큰 관리**: Garmin 토큰은 GitHub Actions 서버에 임시 저장
- **스크린샷**: 디버깅용 스크린샷은 Artifacts에만 저장 (7일 보관)

## 📚 참고 자료

- [python-garminconnect GitHub](https://github.com/cyberjunky/python-garminconnect)
- [Playwright Documentation](https://playwright.dev/python/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

## 🐛 문제 해결

문제가 발생하면 **[BUGFIX_HISTORY.md](BUGFIX_HISTORY.md)**를 참고하세요.

일반적인 문제:
- **로그인 실패**: GitHub Secrets가 올바르게 설정되었는지 확인
- **reCAPTCHA 오류**: 자동 처리되지만 실패 시 스크린샷 확인
- **중복 업로드**: 정상 동작입니다! Garmin이 자동으로 중복 감지합니다.

## 📄 라이선스

개인 사용 목적

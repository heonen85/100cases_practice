# GitHub Actions 설정 가이드

모바일에서 명령을 실행할 수 있도록 GitHub Actions를 설정하는 방법입니다.

## 1단계: GitHub 저장소 생성

### PC에서:
1. GitHub 웹사이트 접속: https://github.com
2. 로그인
3. 우측 상단 "+" → "New repository" 클릭
4. Repository name: `mywhoosh-to-garmin` (또는 원하는 이름)
5. **Private** 선택 (중요: 개인정보 보호)
6. "Create repository" 클릭

### 모바일에서:
1. GitHub 앱 설치 또는 브라우저로 https://github.com 접속
2. 로그인
3. 우측 상단 메뉴 → "New repository"
4. Repository name 입력
5. **Private** 선택
6. "Create repository" 클릭

## 2단계: 코드 업로드

### 방법 1: GitHub 웹 인터페이스 사용 (쉬움)

1. 생성된 저장소 페이지에서 "uploading an existing file" 클릭
2. 프로젝트의 모든 파일을 드래그 앤 드롭
3. Commit message 입력: "Initial commit"
4. "Commit changes" 클릭

### 방법 2: Git 명령어 사용 (PC에서)

```bash
cd /home/heone/100cases_practice/mywhoosh_to_garmin

# Git 초기화
git init
git add .
git commit -m "Initial commit"

# GitHub 저장소 연결 (YOUR_USERNAME을 본인 GitHub 아이디로 변경)
git remote add origin https://github.com/YOUR_USERNAME/mywhoosh-to-garmin.git
git branch -M main
git push -u origin main
```

## 3단계: GitHub Secrets 설정

**중요: 로그인 정보를 안전하게 저장하기 위해 필수입니다!**

### PC 또는 모바일 브라우저에서:

1. GitHub 저장소 페이지로 이동
2. "Settings" 탭 클릭
3. 좌측 메뉴에서 "Secrets and variables" → "Actions" 클릭
4. "New repository secret" 버튼 클릭
5. 다음 4개의 Secret을 하나씩 추가:

#### Secret 1: MYWHOOSH_EMAIL
- Name: `MYWHOOSH_EMAIL`
- Value: `your_mywhoosh_email@example.com`

#### Secret 2: MYWHOOSH_PASSWORD
- Name: `MYWHOOSH_PASSWORD`
- Value: `your_mywhoosh_password`

#### Secret 3: GARMIN_EMAIL
- Name: `GARMIN_EMAIL`
- Value: `your_garmin_email@example.com`

#### Secret 4: GARMIN_PASSWORD
- Name: `GARMIN_PASSWORD`
- Value: `your_garmin_password`

**주의: Secret은 한 번 저장하면 다시 볼 수 없으니 정확히 입력하세요!**

## 4단계: GitHub Actions 활성화

1. 저장소 페이지 상단의 "Actions" 탭 클릭
2. 워크플로우가 자동으로 감지되면 "I understand my workflows, go ahead and enable them" 클릭
3. 워크플로우 목록에서 "MyWhoosh to Garmin Sync" 확인

## 5단계: 모바일에서 실행하기

### 모바일 브라우저 (Chrome, Safari 등):

1. GitHub 저장소 접속
2. "Actions" 탭 클릭
3. 좌측에서 "MyWhoosh to Garmin Sync" 클릭
4. 우측 상단 "Run workflow" 버튼 클릭
5. "Run workflow" 확인 버튼 클릭
6. 실행 시작! 🎉

### GitHub 모바일 앱:

1. 앱에서 저장소 열기
2. 하단 탭에서 "Actions" 선택
3. "MyWhoosh to Garmin Sync" 클릭
4. "Run workflow" 버튼 클릭
5. 확인

## 6단계: 실행 결과 확인

1. Actions 탭에서 실행 중인 워크플로우 클릭
2. "sync" job 클릭
3. 각 단계별 로그 확인
4. 성공/실패 여부 확인
5. Artifacts에서 로그 파일 다운로드 가능

## 자동 스케줄링 설정 (선택사항)

매일 자동으로 실행하려면:

1. `.github/workflows/sync.yml` 파일 편집
2. `schedule` 부분의 주석(#) 제거:
   ```yaml
   schedule:
     - cron: '0 21 * * *'  # 매일 오전 6시 (UTC+9 기준)
   ```
3. 파일 저장 및 커밋

**Cron 설정 예시:**
- `0 21 * * *`: 매일 오전 6시 (한국 시간)
- `0 13 * * *`: 매일 오후 10시 (한국 시간)
- `0 22 * * 1`: 매주 월요일 오전 7시 (한국 시간)

## 트러블슈팅

### 1. 워크플로우가 실행되지 않음
- Settings → Actions → General에서 Actions permissions 확인
- "Allow all actions and reusable workflows" 선택

### 2. reCAPTCHA 오류
- MyWhoosh 로그인 시 reCAPTCHA가 나타날 수 있음
- 수동으로 한 번 로그인하면 해결될 수 있음

### 3. Secrets 오류
- Secret 이름이 정확한지 확인 (대소문자 구분)
- Secret 값에 공백이 없는지 확인

### 4. 중복 업로드
- 정상 동작입니다! Garmin이 자동으로 중복 감지합니다.

## 비용

- **완전 무료**: GitHub Actions는 Public/Private 저장소 모두 월 2,000분 무료
- 이 워크플로우는 약 2-5분 소요
- 매일 실행해도 월 150분 정도만 사용 (무료 범위 내)

## 보안

- **Private 저장소 사용 필수**: 코드에 개인정보가 포함되지 않도록
- **Secrets 사용**: 비밀번호가 로그에 노출되지 않음
- **토큰 관리**: Garmin 토큰은 GitHub Actions 서버에 임시 저장

## 추가 팁

### 알림 받기
- GitHub 모바일 앱 설치 시 워크플로우 실패 시 푸시 알림

### 수동 실행 빠른 링크
- 브라우저 북마크에 Actions 페이지 저장
- 모바일 홈 화면에 바로가기 추가

### 로그 확인
- 각 실행마다 로그가 Artifacts에 저장됨
- 7일간 보관 (설정 변경 가능)

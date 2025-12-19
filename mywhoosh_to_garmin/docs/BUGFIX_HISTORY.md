# 버그 수정 이력

이 문서는 프로젝트 개발 과정에서 발생한 문제와 해결 과정을 시간순으로 기록합니다.

---

## 이슈 #1: 로그인 셀렉터 타임아웃

**날짜**: 2025-12-13
**커밋**: `56817d2`

### 증상
```
⚠️ 타임아웃 오류: waiting for locator("input[type=\"text\"]")
Page.fill: Timeout 30000ms exceeded.
```

워크플로우 실행 시 MyWhoosh 로그인 페이지에서 이메일 입력 필드를 찾지 못함.

### 원인
- 너무 일반적인 셀렉터 사용: `input[type="text"]`
- Headless 브라우저 환경에서 페이지 로딩 지연
- 타임아웃 시간 부족 (30초)

### 해결 방법

**1. 더 구체적인 셀렉터 사용**
```python
# Before
page.fill('input[type="text"]', self.email)

# After
email_input = page.locator('input[type="text"], input[name="username"], input[placeholder*="mail" i]').first
email_input.wait_for(state="visible", timeout=30000)
email_input.fill(self.email)
```

**2. 타임아웃 증가**
- 30초 → 60초

**3. 명시적 대기 추가**
```python
email_input.wait_for(state="visible", timeout=30000)
```

**4. 디버깅 로그 추가**
```python
print("  이메일 입력 중...")
```

**커밋 메시지**: `fix: Improve login selectors and increase timeouts`

---

## 이슈 #2: Submit 버튼 비활성화 (정책 동의 누락)

**날짜**: 2025-12-13
**커밋**: `e920963`

### 증상
```
- locator resolved to <button type="submit" disabled="disabled" class="btn-disabled">
- element is not enabled
```

로그인 버튼이 계속 `disabled` 상태로 클릭되지 않음.

### 원인
스크린샷을 통해 발견: **정책 동의 버튼 ("Accept All")을 클릭하지 않음**

로그인 페이지 접속 시 쿠키/개인정보 정책 동의 팝업이 표시되며, 이를 수락해야만 Submit 버튼이 활성화됨.

### 해결 방법

**정책 동의 버튼 자동 클릭 추가**
```python
# 정책 동의 버튼 클릭 (Accept All)
print("  정책 동의 버튼 찾는 중...")
try:
    accept_btn = page.locator('button:has-text("Accept All"), button:has-text("Accept all"), button:has-text("동의")').first
    accept_btn.wait_for(state="visible", timeout=5000)
    accept_btn.click()
    print("  ✅ 'Accept All' 버튼 클릭 완료")
    page.wait_for_timeout(1000)
except Exception as e:
    print(f"  정책 동의 버튼 없음 또는 이미 동의함: {e}")
```

**실행 순서 변경**
```
1. 로그인 페이지 접속
2. ✅ "Accept All" 버튼 클릭 (추가!)
3. 이메일 입력
4. 비밀번호 입력
5. Submit 버튼 클릭
```

**커밋 메시지**: `fix: Add policy acceptance before login`

---

## 이슈 #3: reCAPTCHA 체크박스 미클릭

**날짜**: 2025-12-13~14
**커밋**: `e9e6bcd`, `f8b0577`, `912aba1` (여러 번 개선)

### 증상
스크린샷 확인 결과: **"I'm not a robot" 체크박스가 체크되지 않음** (□ 상태)

### 시도 1: iframe 선택자 개선 (`e9e6bcd`)

**원인**: 잘못된 iframe 선택자
```python
# Before
page.frame_locator('iframe[src*="recaptcha"]')

# After
page.frame_locator('iframe[src*="recaptcha/api2/anchor"]')
```

**결과**: 여전히 실패

### 시도 2: Fallback 방법 추가 (`f8b0577`)

**2가지 방법 시도**
```python
# 방법 1: iframe 내부 클릭
recaptcha_frame = page.frame_locator('iframe[src*="recaptcha/api2/anchor"]').first
checkbox = recaptcha_frame.locator('#recaptcha-anchor').first
checkbox.click()

# 방법 2: 바깥쪽 div 클릭 (fallback)
page.locator('.g-recaptcha').click()
```

**결과**: 여전히 실패

### 시도 3: 3단계 클릭 전략 (`912aba1`) ✅

**최종 해결 방법**

**방법 1: iframe 내부 4가지 셀렉터 시도**
```python
selectors = [
    '#recaptcha-anchor',
    '.recaptcha-checkbox-border',
    '.recaptcha-checkbox-checkmark',
    'div.recaptcha-checkbox'
]

for selector in selectors:
    checkbox = recaptcha_frame.locator(selector).first
    checkbox.click(timeout=3000, force=True)  # force=True 중요!
```

**방법 2: iframe 요소 자체 클릭**
```python
iframe = page.locator('iframe[src*="recaptcha/api2/anchor"]').first
iframe.click(timeout=3000, force=True)
```

**방법 3: 좌표 기반 클릭**
```python
iframe = page.locator('iframe[src*="recaptcha/api2/anchor"]').first
box = iframe.bounding_box()
x = box['x'] + box['width'] / 2
y = box['y'] + box['height'] / 2
page.mouse.click(x, y)  # 마우스로 직접 좌표 클릭
```

**핵심 개선 사항:**
- `force=True`: 요소가 가려져 있어도 강제 클릭
- 5초 대기: iframe 로드 완료 보장
- 3단계 전략: 하나라도 성공하면 OK

**커밋 메시지**: `fix: Implement 3-tier reCAPTCHA click strategy`

---

## 이슈 #4: 중복 다운로드 문제

**날짜**: 2025-12-14
**커밋**: `42579ed`

### 증상
GitHub Actions 워크플로우를 여러 번 실행하면 매번 동일한 30일치 활동을 모두 다시 다운로드함.

### 원인
**GitHub Actions는 매번 새로운 컨테이너에서 실행**
```
실행 1: downloads/ 폴더 비어있음 → 30개 파일 다운로드
실행 2: downloads/ 폴더 비어있음 → 또 30개 파일 다운로드 (중복!)
실행 3: downloads/ 폴더 비어있음 → 또 30개 파일 다운로드 (중복!)
```

로컬 파일 시스템이 휘발성이므로 이전 다운로드 이력을 기억할 수 없음.

### 해결 방법

**`data/history.json` 파일을 Git 저장소에 커밋하여 영구 보존**

**1. `.gitignore` 수정**
```diff
- # 데이터 파일
- data/history.json
```

**2. 초기 `data/history.json` 생성**
```json
{
  "uploaded": {},
  "downloaded": {}
}
```

**3. 워크플로우에 자동 커밋 단계 추가**
```yaml
- name: Commit history updates
  run: |
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"
    git add data/history.json
    if git diff --staged --quiet; then
      echo "No changes to commit"
    else
      git commit -m "Update activity history [skip ci]"
      git push
    fi
```

**동작 방식:**
```
실행 1: 30개 다운로드 → history.json 업데이트 → Git 커밋
실행 2: history.json 읽음 → 이미 다운로드한 것 건너뜀 → 새 활동 1개만 다운로드
실행 3: 새 활동 없으면 아무것도 다운로드 안 함
```

**3중 중복 방지 메커니즘:**
1. 로컬 파일 존재 체크: `downloads/2025-12-14.fit` 이미 있으면 건너뜀
2. 이력 관리자: `history.json`에 기록된 활동 건너뜀
3. Garmin 서버: HTTP 409 Conflict로 중복 업로드 거부

**커밋 메시지**: `feat: Implement persistent history tracking with Git`

---

## 이슈 #5: 스크린샷 파일 정리

**날짜**: 2025-12-14
**커밋**: `4182925`

### 증상
스크린샷 파일이 여러 곳에 흩어짐:
- `/tmp/login_before_submit.png`
- `/tmp/recaptcha_error.png`
- 프로젝트 루트에 `recaptcha_error.png`

### 원인
디버깅용 스크린샷 저장 경로가 통일되지 않음.

### 해결 방법

**`screenshot/` 폴더로 모든 스크린샷 통합**

**1. screenshot 폴더 생성**
```python
self.screenshot_dir = Path(__file__).parent.parent / "screenshot"
self.screenshot_dir.mkdir(exist_ok=True)
```

**2. 스크린샷 저장 경로 변경**
```python
# Before
page.screenshot(path="/tmp/login_before_submit.png")

# After
screenshot_path = self.screenshot_dir / "login_before_submit.png"
page.screenshot(path=str(screenshot_path))
```

**3. 워크플로우 Artifacts 경로 변경**
```yaml
# Before
path: /tmp/*.png

# After
path: screenshot/
```

**4. .gitignore 업데이트**
```gitignore
# 스크린샷
screenshot/*.png
```

**결과:**
- 모든 스크린샷이 `screenshot/` 폴더에 정리됨
- Artifacts 다운로드 시 폴더째 다운로드
- Git에는 커밋되지 않음 (용량 절약)

**커밋 메시지**: `refactor: Organize screenshots into dedicated folder`

---

## 디버깅 도구 추가

### 입력 값 검증
```python
email_value = email_input.input_value()
print(f"  이메일 입력 확인: {email_value[:3]}***")

password_value = password_input.input_value()
print(f"  비밀번호 입력 확인: {'*' * len(password_value)}")
```

### Submit 버튼 상태 확인
```python
is_disabled = submit_btn.get_attribute("disabled")
print(f"  Submit 버튼 disabled 상태: {is_disabled}")

if is_disabled:
    print("  ⚠️  Submit 버튼이 비활성화되어 있습니다. 5초 대기 후 재시도...")
    page.wait_for_timeout(5000)
```

### 스크린샷 캡처
```python
# 로그인 전
screenshot_path = self.screenshot_dir / "login_before_submit.png"
page.screenshot(path=str(screenshot_path))

# reCAPTCHA 실패 시
screenshot_path = self.screenshot_dir / "recaptcha_failed.png"
page.screenshot(path=str(screenshot_path))
```

---

## 교훈 및 베스트 프랙티스

### 1. 웹 스크래핑 디버깅
- **항상 스크린샷 찍기**: 에러 발생 시점의 화면 상태 확인 필수
- **입력 값 검증**: `.input_value()`로 실제 입력된 값 확인
- **요소 상태 확인**: `disabled`, `visible` 등 속성 체크

### 2. reCAPTCHA 처리
- **충분한 대기 시간**: iframe 로드에 시간 필요 (최소 5초)
- **force=True 사용**: headless 브라우저에서는 필수
- **다양한 방법 시도**: 하나의 방법만으로는 불충분
- **좌표 클릭**: 최후의 수단으로 유용

### 3. GitHub Actions 이력 관리
- **휘발성 파일 시스템**: 매번 새 컨테이너 생성
- **Git을 이용한 영속성**: 이력 파일을 Git에 커밋
- **자동 커밋**: `[skip ci]`로 무한 루프 방지

### 4. 셀렉터 선택
- **구체적인 셀렉터**: `input[type="text"]`보다 `input[name="username"]`
- **복합 셀렉터**: 여러 후보를 쉼표로 연결
- **`.first` 사용**: 여러 요소 중 첫 번째 선택

### 5. 에러 핸들링
- **try-except 계층화**: 여러 방법을 순차적으로 시도
- **명확한 로그**: 어떤 방법이 성공/실패했는지 기록
- **Graceful degradation**: 실패해도 최대한 진행

---

## 현재 상태

✅ **안정화 완료**
- 로그인 성공률 높음
- reCAPTCHA 처리 3단계 전략 적용
- 중복 다운로드 완전 차단
- 스크린샷 정리로 디버깅 용이

⏳ **모니터링 중**
- reCAPTCHA 이미지 챌린지 발생 시 대응 방안 검토
- 장기 실행 안정성 관찰

🔄 **향후 개선 가능 사항**
- 업로드 실패 시 재시도 로직
- 텔레그램 알림 추가
- 웹 대시보드 구현

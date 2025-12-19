"""
MyWhoosh 활동 다운로더
"""
import os
from datetime import datetime, timedelta
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


class MyWhooshDownloader:
    """MyWhoosh 웹사이트에서 활동 다운로드"""

    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.download_dir = Path(__file__).parent.parent / "downloads"
        self.download_dir.mkdir(exist_ok=True)
        self.screenshot_dir = Path(__file__).parent.parent / "screenshot"
        self.screenshot_dir.mkdir(exist_ok=True)

    def download_recent_activities(self, days=30):
        """최근 N일간의 활동 다운로드"""
        downloaded_files = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            try:
                # MyWhoosh 로그인
                print(f"  MyWhoosh 로그인 중... ({self.email})")
                page.goto("https://event.mywhoosh.com/auth/login", timeout=60000)
                page.wait_for_load_state("networkidle", timeout=60000)
                page.wait_for_timeout(3000)  # 추가 대기

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

                # 이메일 입력 (더 구체적인 셀렉터)
                print("  이메일 입력 중...")
                email_input = page.locator('input[type="text"], input[name="username"], input[placeholder*="mail" i]').first
                email_input.wait_for(state="visible", timeout=30000)
                email_input.fill(self.email)

                # 입력 확인
                email_value = email_input.input_value()
                print(f"  이메일 입력 확인: {email_value[:3]}***")

                # 비밀번호 입력
                print("  비밀번호 입력 중...")
                password_input = page.locator('input[type="password"]').first
                password_input.wait_for(state="visible", timeout=30000)
                password_input.fill(self.password)

                # 입력 확인
                password_value = password_input.input_value()
                print(f"  비밀번호 입력 확인: {'*' * len(password_value)}")

                # 스크린샷 (디버깅)
                screenshot_path = self.screenshot_dir / "login_before_submit.png"
                page.screenshot(path=str(screenshot_path))
                print(f"  스크린샷 저장: {screenshot_path}")

                # reCAPTCHA 체크박스 클릭 (필수)
                print("  reCAPTCHA 확인 중...")

                # 충분한 대기 시간
                print("  reCAPTCHA 로드 대기 중... (5초)")
                page.wait_for_timeout(5000)

                recaptcha_clicked = False

                # 방법 1: iframe 내부 여러 셀렉터 시도
                try:
                    print("  [방법 1] iframe 내부 클릭 시도...")
                    recaptcha_frame = page.frame_locator('iframe[src*="recaptcha/api2/anchor"]').first

                    # 여러 셀렉터 시도
                    selectors = [
                        '#recaptcha-anchor',
                        '.recaptcha-checkbox-border',
                        '.recaptcha-checkbox-checkmark',
                        'div.recaptcha-checkbox'
                    ]

                    for selector in selectors:
                        try:
                            print(f"    시도 중: {selector}")
                            checkbox = recaptcha_frame.locator(selector).first
                            checkbox.click(timeout=3000, force=True)
                            print(f"    ✅ {selector} 클릭 성공!")
                            recaptcha_clicked = True
                            break
                        except:
                            continue

                    if recaptcha_clicked:
                        page.wait_for_timeout(5000)
                        print("  ✅ reCAPTCHA 처리 완료 (방법 1)")

                except Exception as e:
                    print(f"  ⚠️ 방법 1 실패: {e}")

                # 방법 2: 메인 페이지에서 iframe 전체 클릭
                if not recaptcha_clicked:
                    try:
                        print("  [방법 2] iframe 요소 자체 클릭 시도...")
                        iframe = page.locator('iframe[src*="recaptcha/api2/anchor"]').first
                        iframe.click(timeout=3000, force=True)
                        page.wait_for_timeout(5000)
                        recaptcha_clicked = True
                        print("  ✅ reCAPTCHA 처리 완료 (방법 2)")
                    except Exception as e:
                        print(f"  ⚠️ 방법 2 실패: {e}")

                # 방법 3: 좌표 기반 클릭
                if not recaptcha_clicked:
                    try:
                        print("  [방법 3] iframe 좌표 기반 클릭 시도...")
                        iframe = page.locator('iframe[src*="recaptcha/api2/anchor"]').first
                        box = iframe.bounding_box()
                        if box:
                            # iframe 중앙 클릭
                            x = box['x'] + box['width'] / 2
                            y = box['y'] + box['height'] / 2
                            page.mouse.click(x, y)
                            page.wait_for_timeout(5000)
                            recaptcha_clicked = True
                            print("  ✅ reCAPTCHA 처리 완료 (방법 3)")
                    except Exception as e:
                        print(f"  ⚠️ 방법 3 실패: {e}")

                if not recaptcha_clicked:
                    print("  ⚠️ 모든 reCAPTCHA 클릭 방법 실패")
                    screenshot_path = self.screenshot_dir / "recaptcha_failed.png"
                    page.screenshot(path=str(screenshot_path))
                    print(f"  실패 스크린샷: {screenshot_path}")

                # Submit 버튼 상태 확인
                submit_btn = page.locator('button[type="submit"]').first
                is_disabled = submit_btn.get_attribute("disabled")
                print(f"  Submit 버튼 disabled 상태: {is_disabled}")

                if is_disabled:
                    print("  ⚠️  Submit 버튼이 비활성화되어 있습니다. 5초 대기 후 재시도...")
                    page.wait_for_timeout(5000)
                    is_disabled = submit_btn.get_attribute("disabled")
                    print(f"  재확인 - Submit 버튼 disabled 상태: {is_disabled}")

                # 로그인 버튼 클릭
                print("  로그인 버튼 클릭...")
                submit_btn.click()
                page.wait_for_load_state("networkidle", timeout=60000)
                page.wait_for_timeout(3000)

                # Activities 페이지로 이동
                print("  Activities 페이지 접속 중...")
                page.goto("https://event.mywhoosh.com/user/activities#profile")
                page.wait_for_load_state("networkidle")

                # ACTIVITIES 탭 클릭
                page.click('tab[name="ACTIVITIES"]', timeout=5000)
                page.wait_for_timeout(2000)

                # 활동 목록에서 다운로드
                cutoff_date = datetime.now() - timedelta(days=days)

                # 다운로드 버튼 찾기
                download_buttons = page.locator('button').filter(has_text="download").all()

                print(f"  {len(download_buttons)}개 활동 발견")

                for idx, button in enumerate(download_buttons):
                    # 날짜 추출 (형식: DD/MM/YYYY)
                    row = button.locator('xpath=ancestor::tr')
                    date_cell = row.locator('td').first
                    date_text = date_cell.inner_text().strip()

                    # 날짜 파싱
                    try:
                        activity_date = datetime.strptime(date_text, "%d/%m/%Y")
                    except ValueError:
                        print(f"  ⚠️  날짜 파싱 실패: {date_text}")
                        continue

                    # 기간 체크
                    if activity_date < cutoff_date:
                        print(f"  ⏭️  {date_text} - 기간 초과, 중단")
                        break

                    # 파일명 생성 (YYYY-MM-DD)
                    file_name = activity_date.strftime("%Y-%m-%d") + ".fit"
                    file_path = self.download_dir / file_name

                    # 이미 다운로드했으면 건너뛰기
                    if file_path.exists():
                        print(f"  ⏭️  {date_text} - 이미 존재함")
                        continue

                    # 다운로드
                    print(f"  ⬇️  다운로드 중: {date_text}...")

                    with page.expect_download() as download_info:
                        button.click()

                    download = download_info.value
                    download.save_as(file_path)

                    downloaded_files.append(str(file_path))
                    print(f"  ✅ 저장됨: {file_name}")

            except PlaywrightTimeout as e:
                print(f"  ⚠️  타임아웃 오류: {e}")
            except Exception as e:
                print(f"  ❌ 오류 발생: {e}")
                import traceback
                traceback.print_exc()
            finally:
                browser.close()

        return downloaded_files

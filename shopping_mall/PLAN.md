# 디지털 콘텐츠 쇼핑몰 구축 계획

## 📋 프로젝트 개요

**목표**: 디지털 콘텐츠(전자책, 강의, 소프트웨어 등)를 판매하는 쇼핑몰 웹사이트 구축
**위치**: `100cases_practice/shopping_mall/` (새 프로젝트 폴더)
**예상 기간**: 4주 (풀타임 기준)

---

## 🛠️ 기술 스택 (확정)

### Backend
- **FastAPI** (Python 3.12+)
  - 비동기 지원, 자동 API 문서화, 타입 안정성
  - 현재 프로젝트와 동일한 Python 환경 활용

### Frontend
- **Jinja2 템플릿** (서버 사이드 렌더링)
- **HTMX** (동적 기능, AJAX 대체)
- **TailwindCSS** 또는 순수 CSS

### Database
- **PostgreSQL** (운영 환경)
- **SQLite** (개발 환경)
- **SQLAlchemy 2.0** (ORM, async 지원)

### 결제
- **토스페이먼츠** (국내 1순위)
  - 개발자 친화적 API
  - 샌드박스 무료 제공
  - 수수료: 2.9% + 100원

### 파일 저장
- **로컬 스토리지** (MVP 단계)
- **AWS S3** (확장 단계)

### 인증
- **JWT** (Access Token)
- **Redis** (Refresh Token 저장, 선택)

---

## 📁 프로젝트 구조

```
shopping_mall/
├── app/
│   ├── main.py                  # FastAPI 엔트리포인트 ⭐
│   ├── config.py                # 환경 변수 관리 ⭐
│   ├── api/v1/                  # API 라우터
│   │   ├── auth.py              # 인증 (로그인/회원가입)
│   │   ├── products.py          # 상품 관리
│   │   ├── cart.py              # 장바구니
│   │   ├── orders.py            # 주문/결제
│   │   └── admin.py             # 관리자
│   ├── core/                    # 핵심 로직
│   │   ├── security.py          # JWT, 비밀번호 해싱 ⭐
│   │   ├── payment.py           # 토스페이먼츠 연동 ⭐
│   │   └── file_manager.py      # 파일 업로드/다운로드
│   ├── models/                  # SQLAlchemy 모델
│   │   ├── user.py              # 사용자 ⭐
│   │   ├── product.py           # 상품
│   │   ├── order.py             # 주문
│   │   └── payment.py           # 결제
│   ├── schemas/                 # Pydantic 스키마
│   ├── crud/                    # DB 접근 계층
│   ├── db/                      # DB 설정
│   ├── templates/               # Jinja2 템플릿
│   └── static/                  # CSS/JS/이미지
├── alembic/                     # DB 마이그레이션
├── scripts/                     # 유틸리티 스크립트
├── tests/                       # 테스트
├── uploads/                     # 업로드 파일 (.gitignore)
├── logs/                        # 로그 (.gitignore)
└── docs/                        # 문서
```

---

## 🗄️ 데이터베이스 스키마

### 핵심 테이블

1. **users** (사용자)
   - id, email, hashed_password, full_name
   - is_active, is_admin, created_at

2. **products** (상품)
   - id, category_id, name, slug, description
   - price, file_path, file_size, file_type
   - thumbnail_path, download_limit, is_active

3. **orders** (주문)
   - id, user_id, order_number, total_amount
   - status (pending, paid, completed, refunded)

4. **order_items** (주문 항목)
   - id, order_id, product_id, price, quantity

5. **payments** (결제)
   - id, order_id, pg_tid, method, amount
   - status (pending, approved, failed, canceled)
   - pg_response (JSONB)

6. **download_logs** (다운로드 이력)
   - id, user_id, product_id, order_id
   - download_url, expires_at, downloaded_at
   - ip_address (보안/악용 방지)

7. **categories** (카테고리)
   - id, name, slug, parent_id (계층 구조)

---

## 🚀 단계별 구현 계획

### Phase 1: 환경 설정 (1-2일)

**목표**: 프로젝트 초기화 및 Hello World

#### 작업 항목
1. 폴더 및 가상환경 생성
   ```bash
   mkdir -p shopping_mall && cd shopping_mall
   uv venv && source .venv/bin/activate
   ```

2. 필수 패키지 설치
   ```bash
   uv pip install fastapi[all] uvicorn[standard] sqlalchemy \
     alembic pydantic-settings python-jose[cryptography] \
     passlib[bcrypt] python-multipart aiofiles jinja2 httpx
   ```

3. 기본 파일 생성
   - `app/main.py`: FastAPI 앱 초기화
   - `app/config.py`: Pydantic Settings로 환경 변수 관리
   - `.env.example`: 환경 변수 템플릿
   - `.gitignore`: Git 제외 파일

4. Hello World 테스트
   ```python
   # app/main.py
   from fastapi import FastAPI
   app = FastAPI(title="Digital Shop API")

   @app.get("/")
   async def root():
       return {"message": "Digital Shop API is running"}
   ```

   ```bash
   uvicorn app.main:app --reload
   # http://localhost:8000/docs 확인
   ```

---

### Phase 2: 데이터베이스 및 인증 (3-4일)

**목표**: DB 스키마 생성 및 로그인/회원가입 구현

#### 2.1 데이터베이스 설정 (1일)

1. SQLAlchemy 모델 정의
   - **핵심 파일**: `app/models/user.py`
   - User 모델 생성 (email, password, is_admin 등)

2. Alembic 마이그레이션
   ```bash
   alembic init alembic
   alembic revision --autogenerate -m "Initial tables"
   alembic upgrade head
   ```

3. 초기 데이터 스크립트
   - `scripts/init_db.py`: 관리자 계정 생성

#### 2.2 인증 시스템 (2-3일)

1. JWT 토큰 생성/검증
   - **핵심 파일**: `app/core/security.py`
   - Strava OAuth 패턴 참고 (Access/Refresh Token)

2. 비밀번호 해싱 (bcrypt)

3. API 엔드포인트
   - `POST /api/v1/auth/register`: 회원가입
   - `POST /api/v1/auth/login`: 로그인
   - `GET /api/v1/auth/me`: 현재 사용자 조회

4. 테스트
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"password123"}'
   ```

---

### Phase 3: 상품 및 장바구니 (3-4일)

**목표**: 상품 CRUD 및 장바구니 기능

#### 3.1 상품 관리 (2-3일)

1. 상품 모델 및 CRUD
   - **핵심 파일**: `app/models/product.py`, `app/crud/product.py`

2. API 엔드포인트
   - `GET /api/v1/products/`: 목록 (페이지네이션, 검색)
   - `GET /api/v1/products/{id}`: 상세
   - `POST /api/v1/products/`: 생성 (관리자 전용)
   - `PUT /api/v1/products/{id}`: 수정 (관리자)
   - `DELETE /api/v1/products/{id}`: 삭제 (관리자)

3. 파일 업로드
   - **핵심 파일**: `app/core/file_manager.py`
   - mywhoosh_downloader의 파일 다운로드 패턴 참고
   - 업로드된 파일을 `uploads/products/` 저장

4. 카테고리 API
   - `GET /api/v1/categories/`: 목록

#### 3.2 장바구니 (1일)

1. 장바구니 모델 및 CRUD
   - **핵심 파일**: `app/models/cart.py`

2. API 엔드포인트
   - `GET /api/v1/cart/`: 현재 사용자 장바구니
   - `POST /api/v1/cart/items`: 상품 추가
   - `PUT /api/v1/cart/items/{id}`: 수량 변경
   - `DELETE /api/v1/cart/items/{id}`: 삭제

---

### Phase 4: 결제 시스템 (3-5일)

**목표**: 토스페이먼츠 연동 및 주문 처리

#### 4.1 토스페이먼츠 연동 (2-3일)

1. 토스페이먼츠 클라이언트
   - **핵심 파일**: `app/core/payment.py`
   - REST API 직접 호출 (httpx 사용)

2. 결제 프로세스
   ```
   사용자 → 주문 생성 → 토스 결제창 → 결제 승인 콜백 → 주문 완료
   ```

3. API 엔드포인트
   - `POST /api/v1/orders/`: 주문 생성
   - `POST /api/v1/payments/confirm`: 결제 승인 (토스 콜백)
   - `GET /api/v1/orders/{id}`: 주문 상세

4. 샌드박스 테스트
   - 토스페이먼츠 개발자 계정 생성
   - 테스트 API 키 발급

#### 4.2 주문 상태 관리 (1일)

1. 주문 상태 전이
   ```
   pending → paid → completed
              ↓
           refunded
   ```

2. 트랜잭션 처리
   - 주문 생성 + 재고 차감 (원자성)

#### 4.3 다운로드 링크 생성 (1일)

1. 보안 다운로드 링크
   - 결제 완료 시 일회성 토큰 생성
   - 만료 시간: 48시간
   - 다운로드 횟수 제한: 5회

2. API 엔드포인트
   - `GET /downloads/{token}`: 파일 다운로드 (검증 후)
   - `GET /api/v1/mypage/downloads`: 다운로드 가능 파일 목록

---

### Phase 5: 프론트엔드 (3-4일)

**목표**: 사용자 인터페이스 구현

#### 5.1 템플릿 구조 (1일)

1. 베이스 레이아웃
   - `app/templates/base.html`: 공통 헤더/푸터
   - Jinja2 블록 시스템

2. 정적 파일
   - `app/static/css/main.css`
   - `app/static/js/htmx.min.js`

#### 5.2 주요 페이지 (2-3일)

1. **홈페이지** (`templates/index.html`)
   - 인기 상품, 최신 상품

2. **상품 목록** (`templates/products/list.html`)
   - 카테고리 필터, 검색, 페이지네이션

3. **상품 상세** (`templates/products/detail.html`)
   - 상품 정보, 장바구니 추가, 바로 구매

4. **장바구니** (`templates/cart.html`)
   - 항목 목록, 수량 변경, 삭제

5. **결제 페이지** (`templates/checkout.html`)
   - 주문 요약, 토스페이먼츠 결제창

6. **마이페이지**
   - 주문 내역 (`templates/mypage/orders.html`)
   - 다운로드 가능 파일 (`templates/mypage/downloads.html`)

7. **로그인/회원가입**
   - `templates/auth/login.html`
   - `templates/auth/register.html`

---

### Phase 6: 관리자 기능 (2-3일)

**목표**: 관리자 대시보드 및 상품/주문 관리

#### 6.1 관리자 대시보드 (1일)

1. 통계 페이지
   - 총 매출, 최근 주문, 인기 상품 Top 10

2. 템플릿
   - `templates/admin/dashboard.html`

#### 6.2 상품 관리 (1일)

1. 상품 등록/수정/삭제
   - 파일 업로드 폼
   - 카테고리 선택

2. 템플릿
   - `templates/admin/products.html`

#### 6.3 주문 관리 (1일)

1. 주문 목록 및 상세
   - 검색, 필터, 상태 변경

2. 환불 처리

3. 템플릿
   - `templates/admin/orders.html`

---

### Phase 7: 고급 기능 (선택, 2-3일)

#### 7.1 검색 기능 (1일)
- PostgreSQL Full-Text Search
- 상품명, 설명 검색

#### 7.2 이메일 알림 (1일)
- 회원가입 환영 메일
- 주문 완료 알림
- 다운로드 링크 발송

#### 7.3 보안 강화 (1일)
- Rate Limiting (slowapi)
- HTTPS 강제
- CORS 설정

---

## 🔒 보안 고려사항

### 1. 파일 보안
- **직접 URL 노출 금지**: `/downloads/{token}` 형식 사용
- **다운로드 횟수 제한**: DB에 카운트 기록
- **링크 만료 시간**: 48시간 유효

### 2. 결제 정보 보호
- 토스페이먼츠가 카드 정보 처리 (PCI DSS 준수 불필요)
- 서버에는 결제 결과만 저장
- `.env` 파일 Git 제외

### 3. 개인정보 보호
- 최소 수집 원칙 (이메일, 비밀번호, 이름만)
- 비밀번호 bcrypt 해싱
- 로그에 민감 정보 제외

---

## 📦 배포 계획

### 로컬 개발
```bash
# 1. 환경 변수 설정
cp .env.example .env

# 2. DB 마이그레이션
alembic upgrade head

# 3. 초기 데이터 생성
python scripts/init_db.py

# 4. 개발 서버 실행
uvicorn app.main:app --reload --port 8000
```

### 운영 환경 (예: AWS EC2)
- **웹 서버**: Nginx (리버스 프록시)
- **앱 서버**: Gunicorn + Uvicorn Workers
- **데이터베이스**: PostgreSQL
- **캐시**: Redis (선택)

### GitHub Actions CI/CD
- 테스트 자동 실행
- 배포 자동화

---

## 📅 예상 일정

```
Week 1: 환경 설정 + 인증 시스템 + 상품 관리 API
Week 2: 장바구니 + 토스페이먼츠 연동 + 주문 시스템
Week 3: 프론트엔드 템플릿 + 관리자 페이지
Week 4: 테스트 + 버그 수정 + 배포 준비
```

**총 예상 기간**: 4주 (풀타임 기준)

---

## 💰 예상 비용

### 개발 단계
- 모든 도구 및 라이브러리: **무료**
- 토스페이먼츠 샌드박스: **무료**

### 운영 단계 (월 기준)
- AWS EC2 t3.small: $15
- RDS PostgreSQL db.t3.micro: $15
- 도메인 (.com): $1/월 (연 $12)
- SSL 인증서 (Let's Encrypt): **무료**
- 토스페이먼츠 수수료: **매출의 2.9% + 거래당 100원**

**총 초기 비용**: 약 $30/월 + 거래 수수료

---

## 📌 핵심 파일 (구현 시작 순서)

구현 시 가장 먼저 생성해야 할 파일 5개:

1. **`shopping_mall/app/main.py`**
   - FastAPI 엔트리포인트
   - 라우터 등록, CORS 설정

2. **`shopping_mall/app/config.py`**
   - Pydantic Settings로 환경 변수 관리
   - DB_URL, SECRET_KEY, TOSS_SECRET_KEY

3. **`shopping_mall/app/models/user.py`**
   - 사용자 테이블 정의
   - 모든 모델의 외래 키 참조 대상

4. **`shopping_mall/app/core/security.py`**
   - JWT 토큰 생성/검증
   - 비밀번호 해싱

5. **`shopping_mall/app/core/payment.py`**
   - 토스페이먼츠 API 래퍼
   - 결제 생성, 승인, 취소

---

## ✅ 시작 전 체크리스트

### 설계 확인
- [ ] 기술 스택 최종 승인 (FastAPI, PostgreSQL, 토스페이먼츠)
- [ ] 필수 기능 vs 선택 기능 구분
- [ ] DB 스키마 최종 검토

### 환경 준비
- [ ] 토스페이먼츠 개발자 계정 생성 (https://developers.tosspayments.com/)
- [ ] 샌드박스 API 키 발급
- [ ] PostgreSQL 설치 (또는 Docker)

### 개발 도구
- [ ] Python 3.12+ 설치 확인
- [ ] Git 저장소 생성 (Private 권장)
- [ ] `.env.example` 템플릿 작성

### 학습 자료
- [ ] FastAPI 공식 문서 (https://fastapi.tiangolo.com/)
- [ ] SQLAlchemy 2.0 튜토리얼
- [ ] 토스페이먼츠 API 문서 (https://docs.tosspayments.com/)

---

## 🎯 다음 단계

계획 승인 후:
1. `shopping_mall/` 폴더 생성
2. Phase 1 (환경 설정) 시작
3. Hello World 테스트로 개발 환경 검증
4. Phase 2 (인증 시스템) 구현

**예상 첫 커밋**: "Initial project setup with FastAPI Hello World"

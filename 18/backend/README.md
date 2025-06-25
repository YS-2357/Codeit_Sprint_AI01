# 🎬 Movie Sentiment Review API (FastAPI)

## 📌 프로젝트 개요

본 프로젝트는 영화 정보를 등록하고, 사용자 리뷰에 대해 감성 분석을 수행하는 백엔드 API 서버입니다.  
- **프레임워크**: FastAPI  
- **데이터베이스**: SQLite  
- **감성 분석 모델**: `sangrimlee/bert-base-multilingual-cased-nsmc` (Hugging Face Transformers)

---

## 🧱 기능 구성

### 🎞️ 영화 관련 API

| 기능 | 설명 | 경로 |
|------|------|------|
| 영화 전체 조회 | 등록된 모든 영화 목록 반환 | `GET /movies/` |
| 영화 등록 | 제목, 감독, 장르, 평점, 이미지 URL 포함 | `POST /movies/create_movie` |
| 영화 수정 | ID를 기준으로 영화 정보 수정 | `POST /movies/update_movie` |
| 영화 삭제 | ID 기반 삭제 | `POST /movies/delete_movie` |

---

### 📝 리뷰 관련 API

| 기능 | 설명 | 경로 |
|------|------|------|
| 리뷰 등록 | 감성 분석 수행 후 저장 | `POST /reviews/create` |
| 영화별 리뷰 조회 | 특정 영화의 최근 리뷰 10개 반환 | `GET /reviews/movie/{movie_id}` |

---

### 🧠 감성 분석 모델

- **모델**: Hugging Face의 `sangrimlee/bert-base-multilingual-cased-nsmc`
- **적용 시점**: 리뷰 등록 시 자동 분석
- **출력**: `label` (positive/negative), `score` (0~1 신뢰도)

---

## 🗂️ 프로젝트 구조

```bash
.
├── main.py                 # FastAPI 앱 초기화 및 라우터 등록
├── routers/
│   ├── movies.py          # 영화 관련 API 라우터
│   └── reviews.py         # 리뷰 관련 API 라우터
├── movie_db.py            # 영화 DB 조작 함수
├── review_db.py           # 리뷰 DB 조작 함수
├── schema.py              # Pydantic 데이터 모델 정의
├── model.py               # 감성 분석 모델 로드 함수
├── utils.py               # 공통 유틸리티 (로거, 전처리)
├── db/
│   ├── movies.db          # 영화 DB (SQLite)
│   └── reviews.db         # 리뷰 DB (SQLite)
```

## 🧪 실행 방법

```bash
# 의존성 설치
pip install -r requirements.txt

# FastAPI 실행
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

## 🔍 예시 요청 및 응답

### 1. 영화 등록
```bash
POST /movies/create_movie
Content-Type: application/json

{
  "title": "기생충",
  "director": "봉준호",
  "category": "드라마",
  "rating": 4.5,
  "image_url": "https://image.com/parasite.jpg"
}
```

### 2. 리뷰 등록
```bash
POST /reviews/create
Content-Type: application/json

{
  "movie_id": 1,
  "reviewer": "홍길동",
  "content": "정말 재미있고 몰입감 넘치는 영화였습니다!"
}
```

응답:

```json
{
  "message": "홍길동님의 리뷰가 등록되었습니다.",
  "sentiment": {
    "label": "positive",
    "score": 0.998
  }
}
```

## 🧠 ERD (데이터베이스 구조도)

### 🎞️ Movie

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| id | INTEGER | PK, AUTOINCREMENT |
| title | TEXT | 영화 제목 |
| director | TEXT | 감독 이름 |
| category | TEXT | 장르 |
| rating | REAL | 평점 (0~5) |
| image_url | TEXT | 포스터 이미지 URL |

### 📝 Review

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| id | INTEGER | PK, AUTOINCREMENT |
| movie_id | INTEGER | FK (movie.id 참조) |
| reviewer | TEXT | 작성자 |
| content | TEXT | 리뷰 내용 |
| sentiment_label | TEXT | 감성 분류 (positive/negative) |
| sentiment_score | REAL | 감성 점수 (0~1) |
| created_at | TEXT | 작성일 (자동 생성) |

---

## 🔒 기타

- 로깅: `utils.get_logger`를 통해 DEBUG 레벨 이상의 로그 출력
- 전처리: `clean_text`로 리뷰 내용의 불필요한 문자 제거
- 라우터 모듈화: `/routers` 폴더로 API 논리 분리
- DB 경로: `db/movies.db`, `db/reviews.db` (로컬 SQLite)

---

## 📎 FastAPI 문서 확인

서버 실행 후 브라우저에서 다음 주소로 접속하면 API 문서를 확인할 수 있습니다:

[**http://127.0.0.1:8000/docs**](http://127.0.0.1:8000/docs)

---

## 👏 기여자

- 정영선
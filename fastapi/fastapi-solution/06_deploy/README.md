# 영화 리뷰 서비스

FastAPI 백엔드와 Streamlit 프론트엔드로 구성된 영화 리뷰 서비스입니다.
KoBERT 모델을 사용하여 리뷰의 감정 분석 기능을 제공합니다.

## 기능
- 영화 리스트 조회
- 영화 검색
- 영화 리뷰 추가 및 조회
- KoBERT를 활용한 리뷰 감정 분석 (기쁨, 슬픔, 분노, 두려움, 따뜻함)
- 영화 추가/수정/삭제

## 기술 스택
- **백엔드**: FastAPI, transformers, torch
- **프론트엔드**: Streamlit
- **AI 모델**: KoBERT (한국어 감정 분석)
- **컨테이너**: Docker, Docker Compose

## Docker로 실행하기

### 1. Docker Compose로 전체 서비스 실행
```bash
# 이미지 빌드 및 컨테이너 실행
docker-compose up --build

# 백그라운드에서 실행
docker-compose up --build -d

# 서비스 중지
docker-compose down
```

### 2. 개별 Docker 이미지 빌드 및 실행

#### FastAPI 백엔드
```bash
# 이미지 빌드
docker build -t movie-review-backend .

# 컨테이너 실행
docker run -p 8000:8000 movie-review-backend
```

#### Streamlit 프론트엔드
```bash
# 이미지 빌드
docker build -f Dockerfile.streamlit -t movie-review-frontend .

# 컨테이너 실행 (FastAPI 서버가 실행 중이어야 함)
docker run -p 8501:8501 movie-review-frontend
```

## 로컬 개발 환경에서 실행하기

### 1. 의존성 설치
```bash
# uv 사용 (권장)
uv pip install -e .

# 또는 pip 사용
pip install -e .
```

### 2. 서버 실행
```bash
# FastAPI 백엔드 실행
uvicorn main:app --reload

# Streamlit 프론트엔드 실행 (새 터미널에서)
streamlit run streamlit.py
```

## 접속 URL
- **FastAPI (백엔드)**: http://localhost:8000
- **FastAPI 문서**: http://localhost:8000/docs
- **Streamlit (프론트엔드)**: http://localhost:8501

## API 엔드포인트
- `GET /movies` - 모든 영화 조회
- `GET /movies/{movie_title}` - 특정 영화 조회
- `GET /movies/{movie_title}/reviews` - 특정 영화의 리뷰 조회
- `POST /movies/{movie_title}/reviews` - 리뷰 추가 (자동 감정 분석)
- `POST /predict` - 텍스트 감정 분석
- `POST /movies/create_movie` - 영화 추가

## 프로젝트 구조
```
06_deploy/
├── main.py                 # FastAPI 백엔드
├── streamlit.py           # Streamlit 프론트엔드
├── pyproject.toml         # Python 의존성
├── Dockerfile             # FastAPI용 Dockerfile
├── Dockerfile.streamlit   # Streamlit용 Dockerfile
├── docker-compose.yml     # Docker Compose 설정
├── .dockerignore         # Docker 빌드 제외 파일
└── README.md             # 프로젝트 문서
```

## 주의사항
- 최초 실행 시 KoBERT 모델 다운로드로 인해 시간이 소요될 수 있습니다.
- Docker 환경에서는 모델 캐시를 위해 볼륨 마운트를 사용합니다.
- 메모리 사용량이 높을 수 있으므로 충분한 시스템 리소스를 확보해주세요.

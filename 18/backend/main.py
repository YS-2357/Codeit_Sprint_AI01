from fastapi import FastAPI
from routers import movies, reviews
from model import load_model
from utils import get_logger

app = FastAPI()
logger = get_logger(__name__)

# 감성 분석 모델
logger.debug("🛠️ 감성 분석 모델 로드 시작")
app.state.sentiment_model = load_model()
logger.info("✅ 감성 분석 모델 로드 완료")

# 라우터 등록
logger.debug("🛠️ 라우터 등록 시작")
app.include_router(movies.router)
app.include_router(reviews.router)
logger.info("✅ 라우터 등록 완료")

@app.on_event("startup")
def startup_event():
    logger.info("✅ FastAPI 서버 시작")

@app.get("/")
def read_root():
    logger.debug("🛠️ 루트 경로 '/' 요청 수신")
    return {"message": "영화 정보 API 입니다."}
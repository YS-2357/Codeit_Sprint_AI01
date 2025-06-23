from fastapi import FastAPI
from routers import movies, reviews
from sentiment import load_model

app = FastAPI()

# 감성 분석 모델
load_model()

# 라우터 등록
app.include_router(movies.router)
# app.include_router(reviews.router)

@app.get("/")
def read_root():
    return {"message": "영화 정보 API 입니다."}
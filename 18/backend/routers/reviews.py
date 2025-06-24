from fastapi import APIRouter, HTTPException, Request
from schema import Review
from utils import get_logger, clean_text
from review_db import insert_review, fetch_reviews_by_movie

logger = get_logger(__name__)
router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("/create")
async def create_review(request: Request, review: Review):
    logger.debug(f"🛠️ {review.reviewer}님의 리뷰 등록 요청: {review.content}")
    try:
        cleaned_content = clean_text(review.content)
        logger.debug(f"🛠️ 전처리된 리뷰 내용: {cleaned_content}")
        model = request.app.state.sentiment_model
        result = model(cleaned_content)[0]  # 예: {'label': 'positive', 'score': 0.998}
        logger.debug(f"🛠️ 감성 분석 결과: {result}")
        review.sentiment_label = result["label"]
        review.sentiment_score = result["score"]

        insert_review(review)
        logger.info(f"✅ 리뷰 등록 성공 | 감성: {result['label']} (신뢰도: {result['score']:.3f})")
        return {
            "message": f"{review.reviewer}님의 리뷰가 등록되었습니다.",
            "sentiment": result
        }
    
    except Exception as e:
        logger.error(f"❌ 리뷰 등록 실패: {e}")
        raise HTTPException(status_code=500, detail="리뷰 등록에 실패했습니다.")


@router.get("/movie/{movie_id}")
async def get_reviews(movie_id: int):
    logger.debug(f"🛠️ 리뷰 조회 요청 (movie_id={movie_id})")
    reviews = fetch_reviews_by_movie(movie_id)
    logger.info(f"✅ 리뷰 조회 완료")
    return reviews
from fastapi import APIRouter, HTTPException
from schema import Movie, MovieID
from utils import get_logger
from movie_db import fetch_all_movies, insert_movie, delete_movie, update_movie

logger = get_logger(__name__)
router = APIRouter(prefix="/movies", tags=["Movies"])


@router.get("/")
async def read_all_movies():
    logger.debug("🛠️ 영화 목록 조회 요청")
    movies = fetch_all_movies()
    logger.info(f"✅ 총 {len(movies)}개의 영화 반환됨")
    return movies


@router.post("/create_movie")
async def create_movie_api(new_movie: Movie):
    logger.debug(f"🛠️ 영화 등록 요청: {new_movie}")
    try:
        insert_movie(new_movie)
        logger.info(f"✅ 영화 등록 성공: {new_movie.title}")
        return {"message": f"{new_movie.title} 영화가 추가되었습니다."}
    except ValueError as ve:
        logger.warning(f"⚠️ 영화 등록 실패 (중복): {new_movie.title}")
        raise HTTPException(status_code=400, detail=str(ve))


@router.post("/update_movie")
async def update_movie_api(movie: Movie):
    logger.debug(f"🛠️ 수정 요청: {movie}")
    updated = update_movie(movie)
    if updated == 0:
        logger.warning(f"⚠️ 수정 실패 - 존재하지 않음: {movie.title} by {movie.director}")
        raise HTTPException(status_code=404, detail="수정할 영화가 존재하지 않습니다.")
    logger.info(f"✅ 영화 수정 완료: {movie.title}")
    return {"message": f"{movie.title} 영화 정보가 수정되었습니다."}


@router.post("/delete_movie")
async def delete_movie_api(movie: MovieID):
    logger.debug(f"🛠️ 삭제 요청: {movie.id}")
    deleted = delete_movie(movie.id)
    if deleted == 0:
        logger.warning(f"⚠️ 삭제 실패 - 대상 없음: {movie.id}")
        raise HTTPException(status_code=404, detail="해당 영화가 존재하지 않습니다.")
    logger.info(f"✅ 영화 삭제 완료: {movie.id}")
    return {"message": f"{movie.id} 영화가 삭제되었습니다."}
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import fetch_all_movies, insert_movie

router = APIRouter(prefix="/movies", tags=["Movies"])

class Movie(BaseModel):
    title: str
    director: str
    category: str
    rating: float | None = None
    image_url: str | None = None

@router.get("/")
async def read_all_movies():
    return fetch_all_movies()

@router.post("/create_movie")
async def create_movie(new_movie: Movie):
    insert_movie(new_movie.dict())
    return {"message": f"{new_movie.title} 영화가 추가되었습니다."}
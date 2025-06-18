from fastapi import FastAPI,HTTPException,Query,Path
from typing import Annotated,Optional,Dict
from pydantic import BaseModel, Field
from typing import  List
import os
from fastapi import Depends, FastAPI, HTTPException, Query , Body
from sqlmodel import Field, Session, SQLModel, create_engine, select, and_
from contextlib import asynccontextmanager


"""
사전에 저장된 테이블을 불러와서 쿼리날려보기

"""


sqlite_file_name = "movies.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    if os.path.exists(sqlite_file_name):
        return
    SQLModel.metadata.create_all(engine)


def get_session():
    '''
    Session :데이터베이스와의 상호작용을 관리하는 객체
    '''
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("애플리케이션이 시작되었습니다!")
    create_db_and_tables()
    yield
    print("애플리케이션이 종료되었습니다!")


app = FastAPI(lifespan=lifespan)

class Movie(BaseModel):
    '''
    필드형 정의
    '''
    id: int | None = Field(description='ID 중복불가', default=None)   # python 3.10버전 이상부터 지원, 이전에는 Union[float, None] 이런방식으로 사용
    title: str = Field(min_length=1, description='제목')
    director: str = Field(min_length=1, description='감독')
    category: str = Field(min_length=1, description='카테고리')
    rating: float | None = Field(default=None, description='평점')
    image_url: str | None = Field(default=None, description='포스터')


class MovieRequest(Movie):

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "title": "범죄도시5",
                "director": "마동석",
                "category": "액션",
                "rating": 5,
                'image_url': 'https://image.com/movie.jpg'
            }
        }
    }
        


class MoviesTable(SQLModel, table=True):
    __tablename__ = "movie" # 테이블에서 저장된 이름으로 저장
    id: Optional[int] = Field(default=None, primary_key=True, description='ID 중복불가')
    title: str = Field(min_length=1, description='제목')
    director: str = Field(min_length=1, description='감독')
    category: str = Field(min_length=1, description='카테고리')
    rating: Optional[float] = Field(default=None, description='평점')
    image_url: Optional[str] = Field(default=None, description='포스터')


        
@app.get("/",description='처음!',response_description='환영 메시지')
async def read_root():
    return {"message": "Hello, World!"}

@app.get("/movies")
async def read_all_movies(session: SessionDep):
    movies = session.exec(select(MoviesTable)  
                          ).all()
    
    print(movies)
    return movies

@app.get('/movies/{movie_title}')
async def read_movie(session: SessionDep, movie_title: Annotated[str,Path( description='영화 제목')]):
    movie = session.exec(select(MoviesTable).where(MoviesTable.title == movie_title)).all() # 특정 ID의 hero 조회
    if movie:
        return movie
    
    raise HTTPException(status_code=404, detail='영화 없음!')

# movies와의 차이 확인해보기
@app.get('/movies/')
async def get_category_by_query(session: SessionDep,category: Annotated[str | None, Query(description='검색 쿼리')] =None):

    movies = session.exec(select(MoviesTable).where(MoviesTable.category == category)).all() # 특정 ID의 hero 조회
    return movies

@app.get('/movies/bydirector/')
async def get_movies_by_director_path(
    session: SessionDep,
    director: Annotated[str | None, Query()] = None
):
    return session.exec(
        select(MoviesTable).where(MoviesTable.director == director)
    ).all()

@app.get('/search/bydirector')
async def get_movies_by_director_path(
    session: SessionDep,
    director: Annotated[str | None, Query()] = None
):
    return session.exec(
        select(MoviesTable).where(MoviesTable.director == director)
    ).all()

@app.get('/movies/search/{movie_director}/')
async def get_director_category_by_query(
    movie_director: str, 
    session: SessionDep,
    category: Annotated[str | None, Query()] = None
):
    return session.exec(
        select(MoviesTable).where(
            and_(
                MoviesTable.director == movie_director,
                MoviesTable.category == category
            )
        )
    ).all()

@app.post('/movies/create_movie')   
async def create_movie(
    new_movie: Annotated[MovieRequest, Body(description='영화추가')],
    session: SessionDep
):  
    
    new_movie = MoviesTable.model_validate(new_movie)  # Pydantic 모델을 SQLModel로 변환

    if not new_movie.title or not new_movie.director:
        raise HTTPException(status_code=400, detail='Title and director are required')
    
    session.add(new_movie)
    session.commit()
    session.refresh(new_movie)
    return new_movie

@app.put('/movies/update_movie')
async def update_movie(updated_movie: Movie, session: SessionDep):
    db_movie = session.exec(
        select(MoviesTable).where(MoviesTable.title == updated_movie.title)
    ).first()
    
    if not db_movie:
        raise HTTPException(status_code=404, detail='영화없음')
    
    # 모든 필드 한번에 업데이트
    db_movie.model_update(updated_movie)
    
    session.add(db_movie)
    session.commit()
    session.refresh(db_movie)
    return db_movie

@app.delete('/movies/delete_movie/{movie_title}')
async def delete_movie(movie_title: str, session: SessionDep):
    movie = session.exec(
        select(MoviesTable).where(MoviesTable.title == movie_title)
    ).first()
    
    if not movie:
        raise HTTPException(status_code=404, detail='영화없음')
    
    session.delete(movie)
    session.commit()
    return {"message": "영화 제거완료"}



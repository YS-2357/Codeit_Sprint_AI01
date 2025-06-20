from fastapi import FastAPI,HTTPException,Query,Path  # FastAPI의 핵심 기능들 불러오기: 웹 서버 생성, 예외 처리, 쿼리/경로 매개변수
from typing import Annotated,Optional,Dict  # Annotated: 의존성 주입 및 메타 정보 표현, Optional: 값이 없을 수도 있음, Dict: 딕셔너리 타입 사용
from pydantic import BaseModel, Field  # Pydantic의 모델 클래스와 필드 정의 도구 (데이터 검증, 문서화 등)
from typing import  List  # List 타입 힌트를 위한 임포트
import os  # 파일 경로 관련 처리를 위한 OS 모듈
from fastapi import Depends, FastAPI, HTTPException, Query , Body  # FastAPI 기능 재호출(중복), Depends: 의존성 주입, Body: 요청 본문 데이터 파싱
from sqlmodel import Field, Session, SQLModel, create_engine, select, and_  
# SQLModel 기반 ORM 기능 임포트: 필드정의, 세션관리, DB연결, 쿼리 작성, 다중조건(where절에서 and연산)

from contextlib import asynccontextmanager  # 비동기 context manager 작성 도구 (FastAPI lifespan에 사용)

"""
사전에 저장된 테이블을 불러와서 쿼리날려보기
"""

# SQLite 데이터베이스 파일명을 정의
sqlite_file_name = "movies.db"
# SQLAlchemy가 사용하는 DB 접속 문자열 구성
sqlite_url = f"sqlite:///{sqlite_file_name}"
# SQLite는 기본적으로 쓰레드 간 연결을 제한하므로 False 설정 필요 (FastAPI에서 필수)
connect_args = {"check_same_thread": False}
# SQLModel이 사용할 DB 연결 객체 생성, echo=True: 실행된 SQL 로그 출력됨
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args,)

# 테이블이 없으면 생성 (DDL 실행)
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# 요청마다 새로운 세션 생성, FastAPI 의존성 주입으로 활용 가능
def get_session():
    with Session(engine) as session:  # SQLModel의 Session 객체를 with문으로 생성 (자동 종료됨)
        yield session  # yield로 값을 전달하여 종속된 함수에 주입

# Annotated를 활용한 세션 의존성 타입 선언, FastAPI 라우트에서 session: SessionDep 형태로 사용
SessionDep = Annotated[Session, Depends(get_session)]

# FastAPI 앱 생명주기 설정, startup/shutdown 이벤트 관리
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()  # 서버 시작 시 DB 테이블이 존재하지 않으면 생성
    yield  # 앱 실행됨
    print("Service down!")  # 앱 종료 시 출력

# Pydantic 기반의 Movie 데이터 모델 정의 (입출력 모델로 사용됨)
class Movie(BaseModel):
    '''
    설명
    '''
    id: int = Field(default=None, description="Primary Key값, 중복 불가")  # 기본키, 생성 시 None이면 DB가 자동 할당
    title: str = Field(description="영화 제목")  # 필수 문자열 필드
    director: str = Field(description="영화 감독")  # 필수 문자열 필드
    category: str = Field(description="영화 장르")  # 필수 문자열 필드
    rating: float | None = None  # 선택적 실수형 필드
    image_url: str | None = None  # 선택적 문자열 (URL 등)

# SQLModel 기반의 ORM 모델 정의. 실제 DB 테이블에 매핑됨
class MoviesTable(SQLModel, table=True):
    __tablename__ = 'movie'  # 테이블 이름 명시 (기본값은 클래스명 소문자)
    id: int | None = Field(description="Primary Key값, 중복 불가", primary_key=True)  # 기본키 필드
    title: str = Field(description="영화 제목")  # 영화 제목 필드
    director: str = Field(description="영화 감독")  # 감독 이름 필드
    category: str = Field(description="영화 장르")  # 장르 필드
    rating: float | None = None  # 평점 필드
    image_url: str | None = None  # 이미지 URL

# 요청 예시를 포함하는 입력용 모델 정의 (예시 JSON 스키마 제공용)
class MovieRequest(Movie):
    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "범죄도시",
                "director": "마동석",
                "category": "액션",
                "rating": 5,
                "image_url": "https://image.com"
            }
        }
    }

# FastAPI 앱 인스턴스 생성
app = FastAPI()

@app.get('/', description='시작 페이지')  # 루트 경로에 GET 요청이 들어오면 hello 메시지를 반환
async def root():
    return {'messages': 'hello'}  # 출력: {"messages": "hello"}

@app.get('/movies', response_model=List[Movie], response_description="적절한 영화 정보 출력")
async def read_all_movies(session: SessionDep):  # 의존성으로 DB 세션을 주입
    movies = session.exec(select(MoviesTable)).all()  # select 쿼리로 전체 영화 목록 조회, list 반환
    return movies  # 반환 시 자동으로 Pydantic(Movie) 객체로 직렬화

@app.get('/movies/{movie_title}', response_model=List[Movie], response_model_exclude=['id'])  # id 제외하고 반환
async def read_movie(session: SessionDep, 
                      movie_title: Annotated[str, Path(description="영화 제목")]):
    # 입력: URL 경로로부터 제목 받음, DB 세션 주입
    movies = session.exec(
        select(MoviesTable).where(MoviesTable.title == movie_title)
    ).all()  # 제목이 일치하는 모든 영화 조회
    if movies:
        return movies  # 결과가 있으면 반환
    raise HTTPException(status_code=404, detail="영화 없음")  # 없으면 404 에러

@app.get('/movies/')
async def get_category_by_query(session: SessionDep, category: Annotated[str | None, Query()] = None):
    '''
    쿼리 파람터로 카테고리(영화 종류)를 받고
    영화 db에서 해당 카테고리 영화가 있다면 리스트 반환
    '''
    if category:
        movies = session.exec(
            select(MoviesTable).where(MoviesTable.category == category)
        ).all()  # 입력: category(str), 출력: 해당 장르의 영화 list
        if movies:
            return movies
    raise HTTPException(status_code=404, detail="영화 없음")  # 없으면 예외

# 감독 이름으로 검색
@app.get('/search')
async def get_direcor_category_by_query(session: SessionDep, director: Annotated[str | None, Query()] = None, category: Annotated[str | None, Query()] = None):
    # 입력: 쿼리 파라미터로 감독과 장르를 받음
    if director and category:
        movies = session.exec(
            select(MoviesTable).where(
                and_(
                    MoviesTable.director == director,
                    MoviesTable.category == category,
                )
            )
        ).all()  # and 조건을 이용해 두 조건 모두 만족하는 영화 조회
        if movies:
            return movies
    raise HTTPException(status_code=404, detail="영화 없음")  # 없으면 404

@app.post('/movies/create_movie')
async def create_movie(session: SessionDep, new_movies: Annotated[MovieRequest, Body(description="영화 추가 요소")] = None):
    '''
    새로운 정보를 추가
    {'id': 1, 'title': '기생충', 'director': '봉준호', 'category': '드라마'}
    - 데이터 검증은 후순위로, 위처럼 데이터가 들어왔다고 가정(id 키를 제외한)
    - id값은 고유하며 데이터베이스에 insert할 경우 생성 (pk)
    '''
    print('11',new_movies)  # 요청 본문에 들어온 new_movies 값 출력
    print('22',type(new_movies))  # <class 'main.MovieRequest'>
    # 입력: MovieRequest (Pydantic 모델) → SQLModel로 변환
    new_movies_MoviesTable = MoviesTable.model_validate(new_movies)  # 데이터 변환 (Pydantic → SQLModel)
    print('33',new_movies_MoviesTable)
    print('44',type(new_movies_MoviesTable))
    session.add(new_movies_MoviesTable)  # DB 세션에 추가
    session.commit()  # 실제 DB 반영
    session.refresh(new_movies_MoviesTable)  # 생성된 PK 등 최신 값으로 갱신
    print('55',new_movies_MoviesTable)
    return {'messages': f'{new_movies_MoviesTable}값이 추가됐습니다.'}  # 최종 메시지 반환

# put
@app.put('/movies/update')
async def update_movie(session: SessionDep, updated_movie: Movie):
    '''
    1. select -> 해당 타이틀을 갖는 영화 검색
    2. session.add(movie)
    3. session.commit()
    '''
    movie = session.exec(
        select(MoviesTable).where(MoviesTable.title == update_movie.title)
    ).first  # 입력: Movie 객체, 출력: 업데이트 대상 row
    print('11',movie)

    '''
    sqlmodel_update 이전 업데이트 하려는 pydantic 인스턴스와 
    class 요소 비교를 통해 누락된 attribute를 추가하고 진행
    '''

    movie.sqlmodel_update(updated_movie)  # SQLModel의 update 메서드로 필드 업데이트
    session.add(movie)  # 갱신된 객체 추가
    session.commit()  # DB 반영
    return {'messages': f'{movie}가 업데이트 되었습니다.'}

# delete
# delete는 브라우저에서 작동하지 않고, curl로 작동된다면 정상적으로 기능함
@app.delete('/movies/delete/{movie_title}')
async def delete_movie(session: SessionDep, movie_title: str):
    '''
    1. select -> 해당 타이틀을 갖는 영화 검색
    2. session.delete(movie)
    3. session.commit()
    '''
    if movie_title:
        movie = session.exec(
            select(MoviesTable).where(MoviesTable.title == movie_title)
        ).first()  # 입력: 제목(str), 출력: 일치하는 row
        print('11',movie)
        session.delete(movie)  # 삭제 대상 설정
        session.commit()  # DB 반영
        return {"messages": f"{movie}가 삭제되었습니다."}
    
    raise HTTPException(status_code=404, detail='해당 제목의 영화가 존재하지 않습니다.')  # 예외 처리
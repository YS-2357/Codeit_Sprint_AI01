
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from contextlib import asynccontextmanager
'''
https://fastapi.tiangolo.com/ko/tutorial/sql-databases/#sqlmodel  기반 작성
https://sqlmodel.tiangolo.com/tutorial/select/#read-data-with-sql SQLModel 공식문서 참고  

uv add sqlmodel

SQLModel은 Pydantic과 SQLAlchemy를 합친 ORM 라이브러리
ORM(Object-Relational Mapping)은 객체 지향 프로그래밍 언어에서 데이터베이스와 상호작용하기 위한 방법론
SQLModel은 Pydantic과 SQLAlchemy를 통합하여 데이터베이스 모델을 정의하고, 데이터베이스와 상호작용할 수 있게 해줌
'''

class Hero(SQLModel, table=True):
    '''
    모델 정의
    primary_key : 기본 키 설정 (중복 불가)
    
    '''
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)
    secret_name: str


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# sqlite에서만 필요한 옵션
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# 요청이 있을 때 마다 새로운 세션 생성
def get_session():
    '''
    Session :데이터베이스와의 상호작용을 관리하는 객체
    '''
    with Session(engine) as session:
        yield session

# 의존성 주입 시스템으로 세션 관리
SessionDep = Annotated[Session, Depends(get_session)]

# Lifespan 이벤트 정의
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup 이벤트: 애플리케이션 시작 시 실행
    print("애플리케이션이 시작되었습니다!")
    # 여기서 DB 연결, 캐시 초기화 등 시작 작업 수행
    create_db_and_tables()
    yield
    # Shutdown 이벤트: 애플리케이션 종료 시 실행
    print("애플리케이션이 종료되었습니다!")
    # 여기서 리소스 정리, DB 연결 종료 등 수행


app = FastAPI(lifespan=lifespan)


''' 레거시방식
## 시작할 떄 데이터 베이스 생성
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
'''

@app.get("/")
def hello() :
    return {'message': 'Hello, World!'}


@app.post("/heroes/")
def create_hero(hero: Hero, session: SessionDep) -> Hero:
    session.add(hero) # Hero 객체 추가
    session.commit()
    session.refresh(hero)
    return hero


@app.get("/heroes/")
def read_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Hero]:
    heroes = session.exec(select(Hero)
                          .offset(offset) # 처음 offset개 건너뛰기
                          .limit(limit)   # limit개까지만 가져오기
                          ).all()
    return heroes


@app.get("/heroes/{hero_id}")
def read_hero(hero_id: int, session: SessionDep) -> Hero:
    hero = session.get(Hero, hero_id) # 특정 ID의 hero 조회
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero


@app.delete("/heroes/{hero_id}")
def delete_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)
    session.commit()
    return {"ok": True}
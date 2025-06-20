# 타입 힌트를 위한 Annotated 사용 (의존성 주입에서 쓰임)
from typing import Annotated

# FastAPI 주요 모듈 불러오기
from fastapi import Depends, FastAPI, HTTPException, Query

# SQLModel 관련 모듈: SQLModel(기본 모델), Field(필드 설정), Session(세션 생성), create_engine(DB 연결), select(쿼리)
from sqlmodel import Field, Session, SQLModel, create_engine, select

# lifespan 관리용 context manager
from contextlib import asynccontextmanager

'''
공식 문서를 기반으로 작성됨
- FastAPI SQLModel 튜토리얼 참고
- SQLModel은 Pydantic(데이터 검증) + SQLAlchemy(ORM)를 통합한 라이브러리
- ORM(Object-Relational Mapping)은 객체지향 언어로 DB를 조작하는 방식
'''

# DB 테이블을 정의할 Hero 모델 클래스 생성
class Hero(SQLModel, table=True):
    '''
    - SQLModel을 상속하며 table=True로 설정해 실제 DB 테이블 생성됨
    - 각 속성은 열(column)을 정의함
    '''
    id: int | None = Field(default=None, primary_key=True)
    # id: 기본키 설정, 자동 증가할 수 있으며 None이면 DB가 자동 할당
    name: str = Field(index=True)
    # name: 문자열 필드이며 인덱스 생성 → 조회 성능 향상
    age: int | None = Field(default=None, index=True)
    # age: 정수형, 비어있을 수 있음(None 허용), 인덱스 생성
    secret_name: str
    # secret_name: 반드시 입력해야 하는 문자열 필드

# SQLite 파일 경로 지정
sqlite_file_name = "database.db"
# SQLAlchemy에서 사용하는 DB 접속 URL 생성
sqlite_url = f"sqlite:///{sqlite_file_name}"

# SQLite의 쓰레드 제약을 해제 (FastAPI의 비동기 처리와 충돌 방지)
connect_args = {"check_same_thread": False}
# DB 엔진 생성 (SQLAlchemy 엔진 객체)
engine = create_engine(sqlite_url, connect_args=connect_args)

# 테이블이 없으면 생성 (DDL 실행)
def create_db_and_tables():
    SQLModel.metadata.create_all(engine, checkfirst=True)
    # SQLModel의 메타데이터를 기반으로 테이블 생성

# 위의 코드 5줄이 database.db를 생성함

# 요청마다 새로운 세션 객체를 생성해서 yield (종료되면 자동 종료)
def get_session():
    '''
    - DB와의 연결을 관리하는 Session 객체 생성
    - yield를 사용하여 종속성 주입(Depends)으로 사용할 수 있도록 함
    '''
    with Session(engine) as session:
        yield session

# 의존성 주입용 타입 선언. Session을 자동으로 주입받음
SessionDep = Annotated[Session, Depends(get_session)]

# lifespan을 이용해 애플리케이션 생명주기(startup/shutdown) 설정
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 애플리케이션 시작 시 호출됨
    print("애플리케이션이 시작되었습니다!")
    create_db_and_tables()  # 시작 시 DB 및 테이블 생성
    yield  # 본체 실행 (FastAPI 앱 실행됨)
    # 애플리케이션 종료 시 호출됨
    print("애플리케이션이 종료되었습니다!")

# FastAPI 앱 생성, lifespan 설정 추가
app = FastAPI(lifespan=lifespan)

'''
레거시 방식의 Startup 이벤트 등록 방식 (현재는 lifespan으로 대체 가능)
@app.on_event("startup")
def on_startup():
    create_db_and_tables()
'''

# 기본 루트 엔드포인트. GET / 요청이 들어올 때 실행됨
@app.get("/")
def hello() :
    return {'message': 'Hello, World!'}
    # 단순히 JSON 형태로 메시지 반환

# Hero 객체를 생성하는 POST 엔드포인트
@app.post("/heroes/")
def create_hero(hero: Hero, session: SessionDep) -> Hero:
    # hero: 요청 본문에서 전달되는 Hero 객체(JSON → 모델 자동 변환)
    # session: DB 세션, 의존성 주입으로 자동 전달됨
    session.add(hero)  # 세션에 hero 객체 추가 (insert 예정 상태)
    session.commit()   # DB에 실제로 저장
    session.refresh(hero)  # DB로부터 최신 상태 갱신 (ex. id 자동 할당)
    return hero  # 저장된 hero 객체 반환 (자동으로 JSON 직렬화됨)

# Hero 객체 목록을 조회하는 GET 엔드포인트
@app.get("/heroes/")
def read_heroes(
    session: SessionDep,  # 의존성 주입된 DB 세션
    offset: int = 0,      # 몇 번째 행부터 시작할지 지정 (페이징 시작점)
    limit: Annotated[int, Query(le=100)] = 100,  # 가져올 최대 개수, 100개 이하로 제한
) -> list[Hero]:
    heroes = session.exec(
        select(Hero)
        .offset(offset)   # offset만큼 건너뛰기
        .limit(limit)     # limit만큼만 조회
    ).all()               # 결과를 모두 리스트로 변환
    return heroes         # Hero 객체 목록 반환

# 특정 Hero의 정보를 조회하는 GET 엔드포인트
@app.get("/heroes/{hero_id}")
def read_hero(hero_id: int, session: SessionDep) -> Hero:
    # hero_id: URL 경로에서 전달되는 ID 값
    # session: 의존성 주입된 DB 세션
    hero = session.get(Hero, hero_id)  # 특정 id를 가진 Hero 검색
    if not hero:
        # 해당 ID가 존재하지 않으면 404 에러 반환
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero  # 해당 Hero 객체 반환

# 특정 Hero를 삭제하는 DELETE 엔드포인트
@app.delete("/heroes/{hero_id}")
def delete_hero(hero_id: int, session: SessionDep):
    # hero_id: URL 경로에서 전달되는 ID 값
    # session: 의존성 주입된 DB 세션
    hero = session.get(Hero, hero_id)  # 해당 ID의 Hero 객체 조회
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)  # Hero 객체 삭제
    session.commit()      # DB 반영
    return {"ok": True}   # 삭제 성공 메시지 반환
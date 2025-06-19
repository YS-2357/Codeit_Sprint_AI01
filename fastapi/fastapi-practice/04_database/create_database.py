from typing import Optional, List
from sqlmodel import Field, SQLModel, create_engine, Session, select
from contextlib import asynccontextmanager
from fastapi import FastAPI
import os

# SQLite 데이터베이스 설정
sqlite_file_name = "movies.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args,)

# Movie 모델 정의 (SQLModel로 데이터베이스 테이블용)
class Movie(SQLModel, table=True):
    # table=True: 데이터베이스 관련으로 사용
    # False or default: pydantic에서 활용했던 것처럼 데이터 검증에 활용 가능
    id: int = Field(default=None, primary_key=True, description='ID 중복불가')
    title: str = Field(min_length=1, description='제목')
    director: str = Field(min_length=1, description='감독')
    category: str = Field(min_length=1, description='카테고리')
    rating: Optional[float] = Field(default=None, description='평점')
    image_url: Optional[str] = Field(default=None, description='포스터')

# 초기 데이터 정의
MOVIES: List[Movie] = [
    Movie(id=1, title='기생충', director='봉준호', category='드라마',image_url = 'https://i.namu.wiki/i/2_Jp0lfl3JYdXu_nslCGz-0Zyx3m6VhU7rp0MbXPSXztm8n-Lb6ORrUnxyAQWpEfWuL2lMn85vK0hLhhuO1_qrf8s8T-2BfRDRx0YzeV8ZrngFoBsE_U-oJrgI9HsWtkkrZcDICKSrsmOR-Yov_kwA.webp'),
    Movie(id=2, title='올드보이', director='박찬욱', category='스릴러',image_url='https://i.namu.wiki/i/PijXoegS_HYyTzyia0VTFryneBNOELoZttOibbi27uAEGD5ddkwh3xL4s1dAuCMkPTUEInIR_cxMS0SccT534bG8Y3Dvp0gMA0nq8d4Y0KxU0IiOAbwY2fbkEh6WVINgpq8VHSPUHop7e28cJFqc2Q.webp'),
    Movie(id=3, title='극한직업', director='이병헌', category='코미디'),
    Movie(id=4, title='범죄도시', director='강윤성', category='액션'),
    Movie(id=5, title='태극기 휘날리며', director='강제규', category='역사'),
    Movie(id=6, title='내부자들', director='이병헌', category='스릴러'),
    Movie(id=7, title='엽기적인 그녀', director='곽재용', category='코미디'),
    Movie(id=8, title='설국열차', director='봉준호', category='드라마')
]

def create_db_and_tables():
    if os.path.exists(sqlite_file_name):
        os.remove(sqlite_file_name)
    
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        existing_movies = session.exec(select(Movie)).all()
        if not existing_movies:
            for movie in MOVIES:
                session.add(movie)
            session.commit()
        else:
            pass


create_db_and_tables()
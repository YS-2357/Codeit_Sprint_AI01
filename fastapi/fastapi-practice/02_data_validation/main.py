from fastapi import FastAPI,HTTPException,Query,Path,Body
from pydantic import BaseModel, Field
from typing import List, Annotated


class Movie(BaseModel):
    '''
    설명
    '''
    id: int = Field(description="Primary Key값, 중복 불가")
    title: str = Field(description="영화 제목")
    director: str = Field(description="영화 감독")
    category: str = Field(description="영화 장르")
    rating: float | None = None
    image_url: str | None = None


class MovieRequest(Movie):
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "title": "범죄도시",
                "director": "마동석",
                "category": "액션",
                "rating": 5,
                "image_url": "https://image.com"
            }
        }
    }
    

app = FastAPI()


MOVIES: List[Movie] = [
    Movie(id=1, title='기생충', director='봉준호', category='드라마'),
    Movie(id=2, title='올드보이', director='박찬욱', category='스릴러'),
    Movie(id=3, title='극한직업', director='이병헌', category='코미디'),
    Movie(id=4, title='범죄도시', director='강윤성', category='액션'),
    Movie(id=5, title='태극기 휘날리며', director='강제규', category='역사'),
    Movie(id=6, title='내부자들', director='이병헌', category='스릴러'),
    Movie(id=7, title='엽기적인 그녀', director='곽재용', category='코미디'),
    Movie(id=8, title='설국열차', director='봉준호', category='드라마')
]

@app.get('/', description='시작 페이지')
async def root():
    return {'messages': 'hello'}

@app.get('/movies', response_model=List[Movie], response_description="적절한 영화 정보 출력")
async def read_all_movies():
    # print('read_all_movies done')
    return MOVIES

@app.get('/movies/{movie_title}', response_model=Movie, response_model_exclude=['id'])  # id값을 제외하고 반환
async def read_movies(movie_title: Annotated[str, Path(description="영화 제목")]):
    for movie in MOVIES:
        if movie.title == movie_title:
            # 태극기 휘날리며의 경우 web상에 넣기 위해서는 태극기%20휘날리며
            return movie
        
    raise HTTPException(status_code=404, detail="영화 없음")

@app.get('/movies/')
async def get_category_by_query(category: Annotated[str | None, Query()] = None):
    '''
    쿼리 파람터로 카테고리(영화 종류)를 받고
    영화 db에서 해당 카테고리 영화가 있다면 리스트 반환
    '''
    print(f"category: {category}")
    # http://127.0.0.1:8000/movies/?category=코미디

    movies_to_return = []
    for movie in MOVIES:
        if movie.category == category:
            movies_to_return.append(movie)

    return movies_to_return


# 감독 이름으로 검색
@app.get('/search')
async def get_direcor_category_by_query(director: Annotated[str | None, Query()] = None, category: Annotated[str | None, Query()] = None):
    
    # http://127.0.0.1:8000/search?director=봉준호&category=드라마
    # 출력: 
    # [
    # {
    #     "id": 1,
    #     "title": "기생충",
    #     "director": "봉준호",
    #     "category": "드라마"
    # },
    # {
    #     "id": 8,
    #     "title": "설국열차",
    #     "director": "봉준호",
    #     "category": "드라마"
    # }
    # ]

    movies_to_return = []
    for movie in MOVIES:
        if movie.director == director and movie.category == category:
            movies_to_return.append(movie)

    return movies_to_return

@app.post('/movies/create_movie')
async def create_movie(new_movies: Annotated[MovieRequest, Body(description="영화 추가 요소")] = None):
    '''
    새로운 정보를 추가
    {'id': 1, 'title': '기생충', 'director': '봉준호', 'category': '드라마'}
    - 데이터 검증은 후순위로, 위처럼 데이터가 들어왔다고 가정(id 키를 제외한)
    - id값은 고유하며 데이터베이스에 insert할 경우 생성 (pk)
    '''

    if not new_movies.title or not new_movies.director\
            or not new_movies.category:
        raise HTTPException(status_code=400, detail='제목, 감독, 카테고리는 필수입니다.')
    
    new_movies.id = len(MOVIES) + 1
    MOVIES.append(new_movies)

    # {"title": "영화1", "director": "봉준호", "category": "역사"}

    return {'messages': f'{new_movies}값이 추가됐습니다.'}


# put
@app.put('/movies/update')
async def update_movie(updated_movie: Annotated[Movie, Body(description="영화 변경 요소")] = None):
    '''
    감독이 개명을 했다?!
    -> 영화 제목으로 기존에 존재하는 데이터에 대해 감독명을 변경해야함

    봉준호 -> 봉준휘
    updated_movie : {"title": "기생충", "director": "봉준휘", "category": "드라마"}
    '''

    for i in range(len(MOVIES)):
        if MOVIES[i].title == updated_movie.title:
            updated_movie['id'] = MOVIES[i].id
            MOVIES[i] = updated_movie
            return {'messages': f'{MOVIES[i]} 변경됨'}

    raise HTTPException(status_code=404, detail='해당 제목의 영화가 존재하지 않습니다.')

# delete
# delete는 브라우저에서 작동하지 않고, curl로 작동된다면 정상적으로 기능함
@app.delete('/movies/delete/{movie_title}')
async def delete_movie(movie_title: str):
    print(movie_title)
    for i in range(len(MOVIES)):
        if MOVIES[i].title == movie_title:
            del MOVIES[i]

            return {'messages': f'{movie_title} 삭제됨'}
        
    raise HTTPException(status_code=404, detail='해당 제목의 영화가 존재하지 않습니다.')
from fastapi import FastAPI,HTTPException,Query,Path,Body
from typing import Annotated
from pydantic import BaseModel, Field
from typing import  List

app = FastAPI()

class MovieBasic(BaseModel):
    id: int 
    title: str
    director: str
    category: str 
    rating: float 
    image_url: str 

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

@app.get("/",description='처음!',response_description='환영 메시지')
async def read_root():
    return {"message": "Hello, World!"}

@app.get("/movies",response_model=List[Movie], description='영화 목록', response_description='영화 목록 반환')
async def read_all_movies():
    return MOVIES

@app.get('/movies/{movie_title}',response_model=Movie, response_model_exclude=["title"])
async def read_movie(movie_title: Annotated[str,Path( description='영화 제목')]):
    for movie in MOVIES:
        if movie.title == movie_title:
            return movie
    raise HTTPException(status_code=404, detail='영화 없음!')

# movies와의 차이 확인해보기
@app.get('/movies/')
async def get_category_by_query(category: Annotated[str | None, Query(description='검색 쿼리')] =None):
    movies_to_return = []
    for movie in MOVIES:
        if movie.category == category:
            movies_to_return.append(movie)
    return movies_to_return

@app.get('/movies/bydirector/')
async def get_movies_by_director_path(director: Annotated[str |None, Query()]=None):
    movies_to_return = []
    for movie in MOVIES:
        if movie.director == director:
            movies_to_return.append(movie)
    return movies_to_return

@app.get('/search/bydirector')
async def get_movies_by_director_path(director:  Annotated[str |None, Query()]=None):
    movies_to_return = []
    for movie in MOVIES:
        if movie.director == director:
            movies_to_return.append(movie)
    return movies_to_return

@app.get('/movies/search/{movie_director}/')
async def get_director_category_by_query(movie_director: str, category:  Annotated[str |None, Query()]=None):
    movies_to_return = []
    for movie in MOVIES:
        if movie.director == movie_director and movie.category == category:
            movies_to_return.append(movie)
    return movies_to_return

# embed 옵션 차이 docs에서 확인해보기
@app.post('/movies/create_movie')   
async def create_movie(new_movie: Annotated[MovieRequest, Body(description='영화추가', embed=True)]):
    if not new_movie.title or not new_movie.director:
        raise HTTPException(status_code=400, detail='Title and director are required')
    new_movie.id = len(MOVIES) + 1
    MOVIES.append(new_movie)
    return new_movie

@app.put('/movies/update_movie')
async def update_movie(updated_movie: Movie):
    for i in range(len(MOVIES)):
        if MOVIES[i].title == updated_movie.title:
            MOVIES[i] = updated_movie
            return MOVIES[i]
    raise HTTPException(status_code=404, detail='영화없음')

@app.delete('/movies/delete_movie/{movie_title}')
async def delete_movie(movie_title: str):
    for i in range(len(MOVIES)):
        if MOVIES[i].title == movie_title:
            del MOVIES[i]
            return {"message": "영화 제거완료"}
    raise HTTPException(status_code=404, detail='영화없음')



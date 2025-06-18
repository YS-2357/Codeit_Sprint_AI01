from fastapi import FastAPI,HTTPException

app = FastAPI()

MOVIES = [
    {'id': 1, 'title': '기생충', 'director': '봉준호', 'category': '드라마'},
    {'id': 2, 'title': '올드보이', 'director': '박찬욱', 'category': '스릴러'},
    {'id': 3, 'title': '극한직업', 'director': '이병헌', 'category': '코미디'},
    {'id': 4, 'title': '범죄도시', 'director': '강윤성', 'category': '액션'},  
    {'id': 5, 'title': '태극기 휘날리며', 'director': '강제규', 'category': '역사'},
    {'id': 6, 'title': '내부자들', 'director': '이병헌', 'category': '스릴러'},
    {'id': 7, 'title': '엽기적인 그녀', 'director': '곽재용', 'category': '코미디'},  
    {'id': 8, 'title': '설국열차', 'director': '봉준호', 'category': '드라마'}  
]

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

@app.get("/movies")
async def read_all_movies():
    return MOVIES

@app.get('/movies/{movie_title}')
async def read_movie(movie_title: str):
    for movie in MOVIES:
        if movie.get('title') == movie_title:
            return movie
    raise HTTPException(status_code=404, detail='영화 없음!')

# movies와의 차이 확인해보기
@app.get('/movies/')
async def get_category_by_query(category: str | None =None):
    movies_to_return = []
    for movie in MOVIES:
        if movie.get('category') == category:
            movies_to_return.append(movie)
    return movies_to_return

@app.get('/movies/bydirector/')
async def get_movies_by_director_path(director: str):
    movies_to_return = []
    for movie in MOVIES:
        if movie.get('director') == director:
            movies_to_return.append(movie)
    return movies_to_return

@app.get('/search/bydirector')
async def get_movies_by_director_path(director: str):
    movies_to_return = []
    for movie in MOVIES:
        if movie.get('director') == director:
            movies_to_return.append(movie)
    return movies_to_return


@app.get('/movies/search/{movie_director}/')
async def get_director_category_by_query(movie_director: str, category: str):
    movies_to_return = []
    for movie in MOVIES:
        if movie.get('director') == movie_director and movie.get('category') == category:
            movies_to_return.append(movie)
    return movies_to_return


@app.post('/movies/create_movie')   
async def create_movie(new_movie: dict):

    if not new_movie.get('title') \
            or not new_movie.get('director') \
            or not new_movie.get('catergory'):
        raise HTTPException(status_code=400, detail='제목과 감독과 카테고리는 필수')
    
    new_movie['id'] = len(MOVIES) + 1
    MOVIES.append(new_movie)
    return new_movie


@app.put('/movies/update_movie')
async def update_movie(updated_movie: dict):
    for i in range(len(MOVIES)):
        if MOVIES[i].get('title') == updated_movie.get('title'):
            MOVIES[i] = updated_movie
            return MOVIES[i]
    raise HTTPException(status_code=404, detail='영화없음')


@app.delete('/movies/delete_movie/{movie_title}')
async def delete_movie(movie_title: str):
    for i in range(len(MOVIES)):
        if MOVIES[i].get('title') == movie_title:
            del MOVIES[i]
            return {"message": "영화 제거완료"}
    raise HTTPException(status_code=404, detail='영화없음')



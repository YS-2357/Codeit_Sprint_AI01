from fastapi import FastAPI,HTTPException
from transformers import AutoTokenizer, BertForSequenceClassification
from fastapi import FastAPI

tokenizer = AutoTokenizer.from_pretrained('monologg/kobert',trust_remote_code=True, resume_download=True)
model = BertForSequenceClassification.from_pretrained('jeonghyeon97/koBERT-Senti5', resume_download=True)


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

# 리뷰 데이터 저장소
REVIEWS = {}

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
async def get_category_by_query(category: str | None = None):
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



@app.post("/predict")
async def predict(text: str):
    # 입력 텍스트 토큰화
    inputs = tokenizer([text], return_tensors='pt', padding=True, truncation=True)

    # 예측
    outputs = model(**inputs)
    predictions = outputs.logits.argmax().item()
    mapper = {  0: 'Angry',
                1: 'Fear',
                2: 'Happy',
                3: 'Tender',
                4: 'Sad'
            }
    
    sentiment = mapper[predictions]
    return {"sentiment": sentiment}


# 영화 리뷰 조회
@app.get('/movies/{movie_title}/reviews')
async def get_movie_reviews(movie_title: str):
    # 영화가 존재하는지 확인
    movie_exists = any(movie.get('title') == movie_title for movie in MOVIES)
    if not movie_exists:
        raise HTTPException(status_code=404, detail='영화 없음!')
    
    return REVIEWS.get(movie_title, [])

# 영화 리뷰 추가 (감정 분석 포함)
@app.post('/movies/{movie_title}/reviews')
async def add_movie_review(movie_title: str, review: dict):
    # 영화가 존재하는지 확인
    movie_exists = any(movie.get('title') == movie_title for movie in MOVIES)
    if not movie_exists:
        raise HTTPException(status_code=404, detail='영화 없음!')
    
    # 리뷰 필수 필드 확인
    if not review.get('author') or not review.get('content'):
        raise HTTPException(status_code=400, detail='작성자와 리뷰 내용은 필수입니다')
    
    # 기존 /predict API를 활용하여 감정 분석 수행
    try:
        sentiment_result = await predict(review['content'])
        review['sentiment'] = sentiment_result['sentiment']
    except Exception as e:
        # 감정 분석 실패 시 Unknown으로 설정
        review['sentiment'] = 'Unknown'
    
    # 리뷰 ID 생성
    if movie_title not in REVIEWS:
        REVIEWS[movie_title] = []
    
    review['id'] = len(REVIEWS[movie_title]) + 1
    REVIEWS[movie_title].append(review)
    
    return review

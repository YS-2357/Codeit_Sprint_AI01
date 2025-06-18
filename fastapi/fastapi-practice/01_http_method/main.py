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

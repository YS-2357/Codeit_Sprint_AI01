from pydantic import BaseModel, Field

# from typing import Optional, Union
# from enum import Enum

# class MovieCategory(str, Enum):
#     ACTION = "액션"
#     DRAMA = '드라마'
#     COMEDY = '코미디'
#     HORROR = '호러'

class Movie(BaseModel):
    id: int | None = None
    title: str = Field(description='영화 제목', min_length=1, default=None)
    director: str
    category: str
    rating: int = Field(gt=0, le=5)


def main():
    movie = {
        'id': 1, 
        'title': '기생충', 
        'director': '봉준호', 
        'category': '드라마'
    }

    movie_object = Movie(**movie)
    print(movie_object)
    print(type(movie_object))
    print(movie_object.id)
    print(movie_object.model_dump_json())


main()
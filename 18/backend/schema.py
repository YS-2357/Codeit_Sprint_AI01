from pydantic import BaseModel, Field

class Movie(BaseModel):
    id: int | None = Field(default=None, primary_key=True, description="DB에서 자동 생성되는 ID (선택)")
    title: str = Field(..., description="영화 제목을 입력하세요.")
    director: str = Field(..., description="감독 이름을 입력하세요.")
    category: str = Field(..., description="장르를 입력하세요.")
    rating: float | None = Field(
        default=3, 
        gt=0.0, 
        le=5.0,
        description="평점 (0.0 초과, 5.0 이하)"
    )
    image_url: str | None = Field(
        default=None,
        description="포스터 이미지 URL을 입력하세요. 선택 항목입니다."
    )
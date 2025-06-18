FROM python:3.10-slim

# 작업 디렉토리 설정
WORKDIR /app

# Python 의존성 파일 복사
COPY pyproject.toml ./
COPY main.py ./

RUN pip install uv
RUN uv pip install --system .

# 포트 노출
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 
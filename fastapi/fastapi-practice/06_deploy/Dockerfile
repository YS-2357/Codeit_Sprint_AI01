FROM python:3.10-slim

WORKDIR /app

COPY pyproject.toml ./
COPY main.py ./

RUN pip install uv
RUN uv pip install --system .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
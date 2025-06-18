## extension

- postman
- sqlite

## 기타명령어

- uv run uvicorn main:app --reload
- uv run --isolated uvicorn main:app --reload (만약 패키지가 없다면 외부 파이썬 참조하는 경우가 있는데 그렇게 동작하지 않도록)
- curl -X GET http://127.0.0.1:8000/hello

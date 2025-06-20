확인사항

pip install uv
uv sync (or uv init -p 3.10) // uv add fastapi uvicorn sqlmodel

1. app 실행으로 database.db 생성여부 확인
   - class Hero 옵션 변경하기
   - 내부 테이블 바뀌는 것 확인

2. sqlite extension으로 스키아 안 테이블 확인
3. post로 적절한 데이터 생성
    - id(pk) 증가 확인
4. 앱 종료 후 다시 실행했을 때 database.db 저장데이터 확인

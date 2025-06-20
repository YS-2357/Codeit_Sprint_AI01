Simple Browser Multi

```bash
# Python 3.10 기반 가상환경, pyproject.toml 및 .venv 폴더 자동 생성
uv init -p 3.10

# FastAPI, Uvicorn, Streamlit, requests를 설치하고 pyproject에 등록
uv add fastapi uvicorn streamlit requests

# main.py의 app 객체로 FastAPI 실행, --reload는 코드 수정 자동 반영
uv run uvicorn main:app --reload

# Streamlit 앱 실행 (http://localhost:8501), FastAPI 서버가 먼저 켜져 있어야 정상 동작


uv run streamlit run streamlit.py
```
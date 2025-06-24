import streamlit as st
from utils import get_logger

st.set_page_config(page_title="영화 리뷰 분석", layout="wide")

logger = get_logger(__name__)
logger.info("✅ Streamlit 앱 시작")

st.title("🎬 영화 리뷰 분석 App")
st.markdown("""
안녕하세요! 이 앱은 FastAPI와 Streamlit을 활용해 만든 **영화 리뷰 감성 분석 플랫폼**입니다.

좌측의 메뉴에서 다음 기능을 사용할 수 있습니다:
- 📽️ **영화 등록 및 목록 조회**
- ✏️ **리뷰 등록 및 감성 분석 결과 확인**
""")

logger.debug("🛠️ 메인 페이지 UI 렌더링 완료")
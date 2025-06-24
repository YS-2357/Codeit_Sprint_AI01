import streamlit as st
import requests
from utils import get_logger

logger = get_logger(__name__)

# API_URL = "http://backend:8000"
API_URL = "http://127.0.0.1:8000"

st.title("📽️ 영화 관리")
logger.info("✅ 영화 페이지 로드 완료")

# 상태 변수로 갱신 여부 제어
if "refresh_movies" not in st.session_state:
    st.session_state.refresh_movies = False

# 영화 등록이 끝난 후 True로 설정되면 목록 재요청
if st.session_state.refresh_movies:
    logger.debug("🛠️ 영화 목록 갱신 요청 감지됨")
    st.session_state.refresh_movies = False  # 초기화
    st.rerun()

st.subheader("🎞️ 영화 목록")

try:
    res = requests.get(f"{API_URL}/movies/")
    logger.debug("🛠️ 영화 목록 API 요청 완료")
    if res.status_code == 200:
        movies = res.json()
        if movies:
            cols = st.columns(3)
            for idx, movie in enumerate(movies):
                with cols[idx % 3]:
                    st.image(movie["image_url"], width=160)
                    st.markdown(f"**🎬 {movie['title']}**")
                    st.caption(f"👤 {movie['director']}  |  🏷️ {movie['category']} | 🍅 {movie['rating']}")
            logger.info(f"✅ 총 {len(movies)}개의 영화 표시됨")
        else:
            st.info("등록된 영화가 없습니다.")
            logger.info("✅ 영화 목록이 비어있음")
    else:
        st.error("영화 목록 조회 실패")
        logger.error(f"❌ 영화 목록 요청 실패 - 상태코드: {res.status_code}")
except Exception as e:
    st.error(f"요청 실패: {e}")
    logger.exception(f"❌ 영화 목록 요청 중 예외 발생: {e}")

# 🎬 영화 등록
st.divider()
st.subheader("🎬 영화 등록")
with st.form("movie_form"):
    title = st.text_input("제목")
    director = st.text_input("감독")
    category = st.text_input("장르")
    rating = st.text_input("평점")
    image_url = st.text_input("포스터 URL")
    submitted = st.form_submit_button("등록하기")

    if submitted:
        if not all([title, director, category, rating, image_url]):
            st.warning("모든 항목을 입력해주세요.")
            logger.warning("⚠️ 필수 입력 누락")
        else:
            payload = {
                "title": title,
                "director": director,
                "category": category,
                "rating": rating,
                "image_url": image_url
            }
            logger.debug(f"🛠️ 영화 등록 페이로드: {payload}")
            try:
                res = requests.post(f"{API_URL}/movies/create_movie", json=payload)
                if res.status_code == 200:
                    st.success(res.json()["message"])
                    st.session_state.refresh_movies = True  # 목록 다시 불러오기 트리거
                    logger.info("✅ 영화 등록 성공 및 목록 갱신 트리거")
                else:
                    st.error(f"오류 - {res.status_code}: {res.text}")
                    logger.error(f"❌ 영화 등록 실패 - {res.status_code}: {res.text}")
            except Exception as e:
                st.error(f"요청 실패: {e}")
                logger.exception(f"❌ 영화 등록 중 예외 발생: {e}")
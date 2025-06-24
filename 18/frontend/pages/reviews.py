import streamlit as st
import requests
from utils import get_logger

logger = get_logger(__name__)

# API_URL = "http://backend:8000"
API_URL = "http://127.0.0.1:8000"

st.title("✏️ 리뷰 등록 및 조회")
logger.info("✅ 리뷰 페이지 로드 완료")

# 영화 목록 불러오기
try:
    res = requests.get(f"{API_URL}/movies/")
    res.raise_for_status()
    movies = res.json()
    movie_options = {m["title"]: str(m["id"]) for m in movies}
    logger.info(f"✅ 총 {len(movies)}개의 영화 로드됨")
except Exception as e:
    logger.exception(f"❌ 영화 목록 요청 실패: {e}")
    st.error("영화 목록을 불러오지 못했습니다.")
    movie_options = {}

# 리뷰 등록
st.subheader("📝 리뷰 등록")
if movie_options:
    selected_movie_title = st.selectbox("영화 선택", options=movie_options.keys())
    reviewer = st.text_input("작성자")
    content = st.text_area("리뷰 내용")

    if st.button("리뷰 등록"):
        if not reviewer or not content:
            st.warning("작성자와 리뷰 내용을 모두 입력해주세요.")
            logger.warning("⚠️ 리뷰 등록 시 필수 항목 누락")
        else:
            payload = {
                "movie_id": movie_options[selected_movie_title],
                "reviewer": reviewer,
                "content": content
            }
            logger.debug(f"🛠️ 리뷰 등록 페이로드: {payload}")
            try:
                res = requests.post(f"{API_URL}/reviews/create", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    st.success(f"리뷰 등록 완료! 감성: {data['sentiment']['label']}")
                    logger.info("✅ 리뷰 등록 성공")
                else:
                    st.error(f"오류: {res.status_code} - {res.text}")
                    logger.error(f"❌ 리뷰 등록 실패 - {res.status_code}: {res.text}")
            except Exception as e:
                st.error(f"요청 실패: {e}")
                logger.exception(f"❌ 리뷰 등록 중 예외 발생: {e}")

    # 리뷰 조회
    st.divider()
    st.subheader("💬 해당 영화 리뷰 보기")
    selected_movie_id = st.selectbox(
        "리뷰 조회할 영화 선택",
        options=movie_options.values(),
        format_func=lambda k: next(title for title, id_ in movie_options.items() if id_ == k)
    )

    if st.button("리뷰 조회"):
        try:
            response = requests.get(f"{API_URL}/reviews/movie/{selected_movie_id}")
            response.raise_for_status()
            reviews = response.json()
            if not reviews:
                st.info("등록된 리뷰가 없습니다.")
                logger.info(f"✅ 영화 ID {selected_movie_id}에 대한 리뷰 없음")
            else:
                for r in reviews[:10]:  # 최근 10개
                    st.markdown(f"**{r['reviewer']}**: {r['content']} ({r['sentiment_label']}/ {r['created_at']})")
                logger.info(f"✅ 총 {min(10, len(reviews))}개의 리뷰 표시됨")
        except Exception as e:
            st.error(f"조회 실패: {e}")
            logger.exception(f"❌ 리뷰 조회 중 예외 발생: {e}")
else:
    st.warning("등록된 영화가 없습니다. 먼저 영화를 등록해주세요.")
    logger.warning("⚠️ 영화가 없어 리뷰 기능 비활성화됨")
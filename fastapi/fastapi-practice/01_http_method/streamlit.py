import streamlit as st
import requests

# uv run streamlit run streamlit.py

st.title("영화 검색 서비스")

movie_list = requests.get('http://127.0.0.1:8000/movies')

# 프론트엔드로 출력
# st.write(movie_list)
st.write(movie_list.json())
# print(movie_list.json())

st.markdown('---')
st.markdown('</br>', unsafe_allow_html=True)

'''
영화 제목을 입력하여 해당 영화에 대한 정보를 출력해주는 화면 구성
'''
BASE_URL = "http://127.0.0.1:8000/"

movie_title =st.text_input("영화 이름을 입력해주세요:")

if movie_title:
    movie = requests.get(f"{BASE_URL}/movies/{movie_title}")

    if movie.status_code == 200:
        
        st.write(f"감독: {movie.json().get('director')}, \
                 장르: {movie.json().get('category')}")
    else:
        st.write("해당 영화는 존재하지 않습니다.")

# 영화 데이터 추가
# session_state 활용해서 3개의 값을 저장
st.markdown('---')

with st.form(key='movie_form'):
    new_movie = {
        'title': st.text_input('영화 제목'),
        'director': st.text_input('감독'),
        'category': st.text_input('장르')
    }

    submit_button = st.form_submit_button('추가하기')

if submit_button:
    # st.write(new_movie)

    response = requests.post(f'{BASE_URL}/movies/create_movie', json=new_movie)
    if response.status_code == 200:
        st.write('영화가 추가되었습니다.')
    elif response.status_code == 400:
        st.write('적절한 데이터 형식이 아닙니다.')
    else:
        st.write('영화 추가에 실패하였습니다.')

import streamlit as st
import requests

BASE_URL ='http://localhost:8000'

st.write("영화 검색 서비스!")

movie_list = requests.get(f"{BASE_URL}/movies")
st.write(movie_list.json())
st.markdown('---')
st.markdown('</br></br>', unsafe_allow_html=True)


movie_title = st.text_input("영화이름 입력:")

if movie_title:
    movie = requests.get(f"{BASE_URL}/movies/{movie_title}")
    # st.write(movie)
    # st.write(movie.status_code)
    # st.write(movie.json())

    if movie.status_code == 200:
        st.write('감독', movie.json().get('director'))

    elif movie.status_code == 404:
        st.write('영화가 없습니다.')

else:
    st.write("검색하려는 영화 제목을 입력하세요.")


## 영화 데이터 추가
st.markdown('---')
st.markdown('</br></br>', unsafe_allow_html=True)

if st.session_state.get('title') is None:
    st.session_state.title = ""
if st.session_state.get('director') is None:
    st.session_state.director = ""
if st.session_state.get('category') is None:
    st.session_state.category = ""

with st.form(key="movie_form"):

    new_movie = {
        'title': st.text_input("영화 제목", key="title"),
        'director': st.text_input("감독", key="director"),
        'category': st.text_input("카테고리", key="category")
    }
    submit_button = st.form_submit_button("추가하기")


if submit_button:
    response = requests.post(f"{BASE_URL}/movies/create_movie", json=new_movie)
    if response.status_code == 200:
        st.write("영화가 추가되었습니다.")

    else:
        st.write("영화 추가에 실패했습니다.")
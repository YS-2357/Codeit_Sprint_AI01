# caching : 캐시를 로컬에 남기는 것 
# 새로고침을 하더라도 캐시가 남아 있다면 추가 동작하지 않음
# 파일 다운로드 등이 반복적으로 되는것을 막기 위함

import streamlit as st

# # data등에 대한 캐싱
# @st.cache_data
# def down_load_onnx_files(url):
#     data = url
#     return data

# # 데이터 베이스등의 연결을 보전하는 데코레이터
# @st.cache_resource
# def get_database_session(_sessionmaker, url):
#     connection=None
#     return connection


# session state
# 데이터를 공유 및 유지하기 위한 저장공간!

# st.write(st.session_state)


# if 'k' not in st.session_state:
#     st.session_state['k'] = 'v1'

# st.write(st.session_state)


# # attribute 형식으로 입력가능
# if 'k' in st.session_state:
#     st.session_state.k = 'v2'

# st.write(st.session_state)


# st.text_input("Your name", key="name")
# # 이름출력
# st.session_state.name


if 'counter' not in st.session_state:
    st.session_state.counter = 0

button = st.button('클릭')

if button:
    st.session_state.counter +=1

st.write(st.session_state.counter) 
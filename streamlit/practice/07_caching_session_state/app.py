# caching : 캐시를 로컬에 남기는 것 
# 새로고침을 하더라도 캐시가 남아 있다면 추가 동작하지 않음
# 파일 다운로드 등이 반복적으로 되는것을 막기 위함

import streamlit as st

# data등에 대한 캐싱
@st.cache_data
def down_load_onnx_files(url):
    data = url
    return data

# 데이터 베이스등의 연결을 보전하는 데코레이터
@st.cache_resource
def get_database_session(_sessionmaker, url):
    connection=None
    return connection


# session state
# 저장공간

# 딕셔너리 구조와 비슷함
st.session_state['data1'] = 'asno'
st.session_state['data2'] = '2'
st.session_state['data2'] = [1, 2, 3]
st.session_state['data2'] += [4]
st.session_state['data3'] = {'a': 12}

st.write(st.session_state)
if 'data3' in st.session_state:
    st.write(st.session_state['data3']['a'])
else:
    st.write("No data3")

if 'data1' in st.session_state:
    st.write(st.session_state.data1)

# attribute 형식으로 입력가능


# 이름출력

st.text_input('text input: ', key='name')
st.text_input('text input w/ no key')
st.write(st.session_state)


# 버튼 누르면 숫자 증가하는 기능
if "counter" not in st.session_state:
    st.session_state["counter"] = 0

st.button('click', key='click')

if st.session_state.click:
    st.session_state.counter +=1
    
st.write(st.session_state.counter)
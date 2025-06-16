import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from datetime import datetime

########################################################
#################widgets elements#######################
########################################################


# button
button = st.button('button')
st.write(button)

if button:
    st.write('button on')
else:
    st.write('button off')

def say_hello():
    st.write('Hello!')
    return

button_click = st.button('button2', on_click=say_hello)

# download_button
# pandas.DataFrame은 안되고 csv로 바꿔야 가능함
df = pd.DataFrame({'a': [1,2,3]})

data = df.to_csv()

st.download_button(
    label='dataframe', data=data, file_name='df.csv',
    mime='text/csv'
)

# st.write에서 자체적으로 다운로드 기능 지원함
st.write(df)

# uploaded_files -> 403 axios 에러 날 경우 .streamlit 폴더 내 세팅 후 다시 동작
uploaded_files = st.file_uploader(
    'Choose a CSV file'
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        bytes_data = uploaded_file.read()
        st.write("filename :", uploaded_file.name)
        st.write(bytes_data)

# enable_camera -> 크롬에서 확인가능
picture = st.camera_input('camera')
if picture:
    st.image(picture)
    st.write(picture)

    img = Image.open(picture)
    img_array = np.array(img)

    img.save('./save.jpg')

# checkbox
checkbox = st.checkbox('checkbox')
st.write(checkbox)  # True/False

if checkbox:
    st.write('on')

# multi-select
options = st.multiselect(
    'favorite',
    ['apple', 'mango', 'kiwi'],
    default='apple',
)

if options:
    st.write(options)
    st.write(options[0])

# pils
st.pills('pills', [1, 2, 3], selection_mode='single', )

# selectbox
st.selectbox('selectbox', [1, 2, 3, 4])

# slider
st.slider('slider', min_value=0.0, max_value=10.0, value=2.0, step=0.5, format="%.1f")

start_date = st.slider(
    'start data',
    value=datetime(2025, 6, 13, 12, 00),
    format='YY/MM/DD' 
)

# text_input
st.text_input(
    'text input',
    value='Wow! ',
    type='password',
)

# chat_input
chat_history = st.chat_input(
    'chat input',
    accept_file=True
)

if chat_history:
    st.write(chat_history)

# image, 그 외에도 오디오, 비디오 등 가능
st.image(
    'C:/Users/user/Desktop/PythonWorkspace/Codeit_Sprint_AI01/streamlit/practice/05_widgets/cat_sample.jpg',
    caption='cat image'
)
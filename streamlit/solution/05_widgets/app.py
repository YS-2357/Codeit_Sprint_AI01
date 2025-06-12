import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from datetime import datetime

########################################################
#################widgets elements#######################
########################################################


## button
# button = st.button("버튼")
# st.write(button)
# if button:
#     st.write('버튼 눌름')
# else:
#     st.write('버튼 누르지 않음')

# def say_hello():
#     st.write('hi')
#     return 
# button_onclick = st.button('버튼2',on_click=say_hello)


# ## download_button

# # 웹사이트 내부에서 생성한 정보에 대해 로컬 다운로드가 가능하다
# df_csv = pd.DataFrame(
#         np.random.randn(50, 20), columns=("col %d" % i for i in range(20))
#     ).to_csv()

# st.download_button(
#     label="Download CSV",
#     data=df_csv,
#     file_name="data.csv",
#     mime="text/csv",
#     icon=":material/download:",
# )


# ## upload_files -> 403 axios 에러 날 경우 .streamlit 폴더 내 세팅 후 다시 동작
# uploaded_files = st.file_uploader(
#     "Choose a CSV file", accept_multiple_files=True
# )
# for uploaded_file in uploaded_files:
#     bytes_data = uploaded_file.read()
#     st.write("filename:", uploaded_file.name)
#     st.write(bytes_data)


# ## enable_camera -> 크롬에서 확인가능
# picture = st.camera_input("사진촬영")

# if picture:
#     st.image(picture)

#     img = Image.open(picture)
#     img_array = np.array(img)
#     st.write(type(img_array))
#     st.write(img_array.shape)

#     img.save('./save.jpg')



# ## checkbox
# import streamlit as st

# agree = st.checkbox("I agree")
# st.write('before',agree)
# if agree:
#     st.write("Great!")
#     st.write('after',agree)


# ## multi-select
# options = st.multiselect(
#     "What are your favorite colors?",
#     ["Green", "Yellow", "Red", "Blue"],
#     default=["Yellow", "Red"],
# )

# st.write("You selected:", options)
# st.write(options[0])


# ## pils
# options = ["North", "East", "South", "West"]
# selection = st.pills("Directions", options, selection_mode="multi")
# st.markdown(f"Your selected options: {selection}.")


# ## selectbox
# option = st.selectbox(
#     "박스",
#     ("A", "B", "C"),
# st.write("선택한것:", option)

# ## slider
# start_time = st.slider(
#     "시작날짜",
#     value=datetime(2025, 6, 1, 12, 00),
#     format="YY/MM/DD",
# )
# st.write("Start time:", start_time)


# ## text_input
# title = st.text_input("텍스트공간", "기본값") #,type='password'
# st.write("입력된 텍스트 :", title)

# ## chat_input
# prompt = st.chat_input("Say something")
# if prompt:
#     st.write(f"입력: {prompt}")


## image, 그 외에도 오디오, 비디오 등 가능
# st.image("cat_sample.jpg", caption="고양이")
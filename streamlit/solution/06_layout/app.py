import streamlit as st
import numpy as np

## side bar

# with st.sidebar:
#     st.write('사이드바')
#     st.write('사이드바2')

# st.write('사이드바3')

## page config

# st.set_page_config(page_title='타이틀',layout='wide',initial_sidebar_state='collapsed')
# with st.sidebar:
#     st.write('사이드바')
#     st.write('사이드바2')

# st.write('사이드바3')

# col1, col2, col3 = st.columns(3)

# with col1:
#     st.header("A cat")
#     st.image("https://static.streamlit.io/examples/cat.jpg")

# with col2:
#     st.header("A dog")
#     st.image("https://static.streamlit.io/examples/dog.jpg")

# with col3:
#     st.header("An owl")
#     st.image("https://static.streamlit.io/examples/owl.jpg")


# col1, col2 = st.columns([3, 1])
# data = np.random.randn(10, 1)

# col1.subheader("A wide column with a chart")
# col1.line_chart(data)

# col2.subheader("A narrow column with the data")
# col2.write(data)


# # 정렬 관련
# vertical_alignment = st.selectbox(
#     "Vertical alignment", ["top", "center", "bottom"], index=2
# )

# left, middle, right = st.columns(3, vertical_alignment=vertical_alignment)
# left.image("https://static.streamlit.io/examples/cat.jpg")
# middle.image("https://static.streamlit.io/examples/dog.jpg")
# right.image("https://static.streamlit.io/examples/owl.jpg")


# # 라운드 옵션
# left, middle, right = st.columns(3, border=True)

# left.markdown("외부 " * 10)
# middle.markdown("중앙 " * 5)
# right.markdown("오른쪽 ")




# # form
# with st.form("폼테스트"):
#     st.write("폼내부")
#     slider_val = st.slider("슬라이더값")
#     checkbox_val = st.checkbox("체크박스")

#     submitted = st.form_submit_button("제출")
#     if submitted:
#         st.write("슬라이더", slider_val, "체크박스", checkbox_val)
# st.write("폼 바깥")

# # tabs
# tab1, tab2, tab3 = st.tabs(["Cat", "Dog", "Owl"])

# with tab1:
#     st.header("A cat")
#     st.image("https://static.streamlit.io/examples/cat.jpg", width=200)
# with tab2:
#     st.header("A dog")
#     st.image("https://static.streamlit.io/examples/dog.jpg", width=200)
# with tab3:
#     st.header("An owl")
#     st.image("https://static.streamlit.io/examples/owl.jpg", width=200)


## switch_page
# if st.button("Home"):
#     st.switch_page("app.py")
# if st.button("Page 1"):
#     st.switch_page("pages/page_1.py")
# if st.button("Page 2"):
#     st.switch_page("pages/page_2.py")



import streamlit as st
import numpy as np

# page config
st.set_page_config(page_title="page title", initial_sidebar_state="expanded", layout='centered')

# side bar
with st.sidebar:
    st.write('sidebar1')

st.write('sidebar out')

# columns
col1, col2 = st.columns([3, 1])
data = np.random.randn(10, 1)

col1.subheader("A wide column with a chart")
col1.line_chart(data)

col2.subheader("A narrow column with the data")
col2.write(data)

with col1:
    st.header("A cat")
    st.image("https://static.streamlit.io/examples/cat.jpg", width=100)

with col2:
    st.header("A dog")
    st.image("https://static.streamlit.io/examples/dog.jpg", width=100)



# 정렬 관련
vertical_alignment = st.selectbox(
    "Vertical alignment", ["top", "center", "bottom"], index=2
)
left, middle, right = st.columns(3, vertical_alignment=vertical_alignment, border=True)
left.image("https://static.streamlit.io/examples/cat.jpg", width=200)
middle.image("https://static.streamlit.io/examples/dog.jpg", width=200)
right.image("https://static.streamlit.io/examples/owl.jpg", width=200)

# 라운드 옵션(border=True)

# form
with st.form('form'):
    st.write('form inside')

    slider = st.slider('slider')
    checker = st.checkbox('checkbox')

    submit = st.form_submit_button('submit')

    if submit:
        st.write(slider, checker)

st.write(slider, checker)
st.write('form outside')

# tabs

tab1, tab2 = st.tabs(['1', '2'], )

with tab1:
    st.write('tab1 info')

with tab2:
    st.write('tab2 info')

# switch_page
if st.button("Home"):
    st.switch_page("app.py")
if st.button("Page 1"):
    st.switch_page("pages/page1.py")
if st.button("Page 2"):
    st.switch_page("pages/page2.py")
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import time
import matplotlib.pyplot as plt
import random

# write : 단순 작성, 이모지등을 사용 가능
st.write('📌Test :heart: :pencil:')

# 데이터 프레임 출력가능
data_frame = pd.DataFrame(
        {
            "col1": [1, 2, 3, 4],
            "col2": [10, 20, 30, 40],
        }
)

# 변수로도 설정가능
st.write(data_frame)

df = pd.DataFrame(np.random.randn(200, 3), columns=["a", "b", "c"])
# st.write(df)

c = (
    alt.Chart(df)
    .mark_circle()
    .encode(x="a", y="b", size="c", color="c", tooltip=["a", "b", "c"])
)
st.write(c)



### write_stream : streamlit 1.29.0 이상에서
zep_info ="슈퍼캣과 네이버제트의 합작법인 'ZEP'이 운영하는 동명의 메타버스 플랫폼이다. 2021년 11월 30일 베타버전을 시작했으며 2022년 3월 16일 정식서비스를 시작했다. 쉽고 재미있는 메타버스라는 컨셉으로 출발하여 현재 부트캠프, 학교, HRD, 행사, 브랜딩, 오피스 용도로 널리 쓰이고 있으며, 현재는 학교에서 가장 많이 사용되고 있다."
def stream_data():
    for word in zep_info.split(" "):
        yield word + " "
        time.sleep(0.05)

# write_stream
if st.button('stream start'):
    st.write_stream(stream_data)
    

# magic : 변수들을 바로 출력할 수 있도록함
# magic case1

fig, ax = plt.subplots()
ax.plot([1,2], [2,3])
fig

# magic case 2
x = 10
'x =', x

########################################################
#################text elements##########################
########################################################
# title : 타이틀
st.title(":heart: Test")

# header : 헤더 마크다운 
st.header('1')

# subheader : 헤더보다 작음
st.subheader('1.1.')

# markdown : 마크 다운 양식 적용 가능, 크기조절도 가능해서 위 기능들보다 일반적으로 사용
st.markdown('```python```</br> is good', unsafe_allow_html=True)

# badge : 간단한 배지 표기
st.badge(':fire: badge', icon='🔥', color='blue')

# caption: 캡션
st.caption('caption', help='help')

# code: 코드
st.code('''Is it a crown or boat?
                        ii
                      iiiiii
WWw                 .iiiiiiii.                ...:
 WWWWWWw          .iiiiiiiiiiii.         ........
  WWWWWWWWWWw    iiiiiiiiiiiiiiii    ...........
   WWWWWWWWWWWWWWwiiiiiiiiiiiiiiiii............
    WWWWWWWWWWWWWWWWWWwiiiiiiiiiiiiii.........
     WWWWWWWWWWWWWWWWWWWWWWwiiiiiiiiii.......
      WWWWWWWWWWWWWWWWWWWWWWWWWWwiiiiiii....
       WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWwiiii.
          -MMMWWWWWWWWWWWWWWWWWWWWWWMMM-
''', language='python', line_numbers=True, wrap_lines=True)

code_ex = """
def hello():
    print('Hello World!')
"""
st.code(code_ex)

# divider : 구분자 (마크다운으로 해도 됨)
st.divider()

# latex : 수식
st.latex(r'''
    a + ar + a r^2 + a r^3 + \cdots + a r^{n-1} =
    \sum_{k=0}^{n-1} ar^k =
    a \left(\frac{1-r^{n}}{1-r}\right)
    ''')

# html: html 표기 (마크다운으로 해도 됨)
st.html("<p><span style='text-decoration: line-through double red;'>Oops</span>!</p>")




########################################################
#################data elements##########################
########################################################



# 다양한 옵션 # column_config에 넣을 수 있음 (https://docs.streamlit.io/develop/api-reference/data/st.column_config)
df_2 = pd.DataFrame(
    {
        "name": ["Roadmap", "Extras", "Issues"],
        "url": ["https://roadmap.streamlit.app", "https://extras.streamlit.app", "https://issues.streamlit.app"],
        "stars": [random.randint(0, 1000) for _ in range(3)],
        "views_history": [[random.randint(0, 5000) for _ in range(30)] for _ in range(3)],
    }
)
st.dataframe(
    df_2,
    column_config={
        "name": "App name",
        "stars": st.column_config.NumberColumn(
            "Github Stars",
            help="Number of stars on GitHub",
            format="%d ⭐",
        ),
        "url": st.column_config.LinkColumn("App URL"),
        "views_history": st.column_config.LineChartColumn(
            "Views (past 30 days)", y_min=0, y_max=5000
        ),
    },
    hide_index=True,
)
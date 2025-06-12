import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import time
import matplotlib.pyplot as plt
import random

# # write : 단순 작성, 이모지등을 사용 가능
# st.write("Hello, Streamlit!")
# st.write("Hello, :sunglasses:")
# st.write(
#     pd.DataFrame(
#         {
#             "first column": [1, 2, 3, 4],
#             "second column": [10, 20, 30, 40],
#         }
#     )
# )

# # 데이터 프레임 출력가능
# data_frame =    pd.DataFrame(
#         {
#             "col1": [1, 2, 3, 4],
#             "col2": [10, 20, 30, 40],
#         })

# st.write("1 + 1 = ", 2)

# # 변수로도 설정가능
# st.write( data_frame)
# df = pd.DataFrame(np.random.randn(200, 3), columns=["a", "b", "c"])
# c = (
#     alt.Chart(df)
#     .mark_circle()
#     .encode(x="a", y="b", size="c", color="c", tooltip=["a", "b", "c"])
# )

# st.write(c)


# ### write_stream : streamlit 1.29.0 이상에서
# zep_info ="슈퍼캣과 네이버제트의 합작법인 'ZEP'이 운영하는 동명의 메타버스 플랫폼이다. 2021년 11월 30일 베타버전을 시작했으며 2022년 3월 16일 정식서비스를 시작했다. 쉽고 재미있는 메타버스라는 컨셉으로 출발하여 현재 부트캠프, 학교, HRD, 행사, 브랜딩, 오피스 용도로 널리 쓰이고 있으며, 현재는 학교에서 가장 많이 사용되고 있다."
# def stream_data():
#     for word in zep_info.split(" "):
#         yield word + " "
#         time.sleep(0.06)


# # write_stream
# if st.button("스트림 시작"):
#     st.write_stream(stream_data)
    

# # magic : 변수들을 바로 출력할 수 있도록함
# # magic case1

# import matplotlib.pyplot as plt
# import numpy as np

# arr = np.random.normal(1, 1, size=100)
# fig, ax = plt.subplots()
# ax.hist(arr, bins=20)

# fig  
# # plt.show() 안됨! 

# # magic case 2
# x = 10
# 'x', x 


########################################################
#################text elements##########################
########################################################
# title : 타이틀
# header : 헤더 마크다운 
# subheader : 헤더보다 작음
# markdown : 마크 다운 양식 적용 가능, 크기조절도 가능해서 위 기능들보다 일반적으로 사용
# badge : 간단한 배지 표기
# caption: 캡션
# code: 코드
# divider : 구분자 (마크다운으로 해도 됨)
# latext : 수식
# html: html 표기 (마크다운으로 해도 됨)

# st.title("제목이야")
# st.header("헤더", divider="gray")
# st.header("헤더2", divider=True)
# st.subheader("장마시작 is :blue[슬픔] ")


# st.markdown('마크다운')
# st.markdown('# 마크다운')
# st.markdown('마크다운<br>줄바꿈테스트',unsafe_allow_html=True) 

# st.markdown('''
#             마크다운     
#             줄바꿈테스트
#             ''') 


# st.badge("New")
# st.badge("Success", icon=":material/check:", color="green") # https://fonts.google.com/icons?icon.set=Material+Symbols&icon.style=Rounded
# st.badge("search", icon=":material/search:", color="red")

# st.caption("_캡션_ 테스트")

# code = '''def hello():
#     print("Hello, Streamlit!")'''
# st.code(code, language="python")


# st.divider()
# st.markdown('---')


# st.latex(r'''
#     result = \frac{a}{b}
#     ''')

# st.html(
#     '''<div style="color: red;">빨강</div></br>
#     <div style="color: #00FF00;">초록</div>'''
# )


########################################################
#################data elements##########################
########################################################

# np.random.seed(2)
# df = pd.DataFrame(np.random.randn(5, 4), columns=("col %d" % i for i in range(4)))
# st.dataframe(df.style.highlight_max(axis=0)) 


# 다양한 옵션 # column_config에 넣을 수 있음 (https://docs.streamlit.io/develop/api-reference/data/st.column_config)
df = pd.DataFrame(
    {
        "name": ["Roadmap", "Extras", "Issues"],
        "url": ["https://roadmap.streamlit.app", "https://extras.streamlit.app", "https://issues.streamlit.app"],
        "stars": [random.randint(0, 1000) for _ in range(3)],
        "views_history": [[random.randint(0, 5000) for _ in range(30)] for _ in range(3)],
    }
)
st.dataframe(
    df,
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
import streamlit as st
import pandas as pd
import numpy as np
import time
import pydeck as pdk
import plotly.figure_factory as ff

########################################################
#################chart elements#########################
########################################################

chart_data = pd.DataFrame(
    {
        "col1": np.random.randn(20),
        "col2": np.random.randn(20),
        "col3": np.random.choice(["A", "B", "C"], 20),
    }
)

st.area_chart(chart_data, x='col1', y='col2', color='col3')
st.bar_chart(chart_data, x='col3', y='col1', horizontal=True)
st.line_chart(chart_data, x='col3', y='col2', )
st.scatter_chart(chart_data, x='col1', y='col2')



df1 = pd.DataFrame(
    np.random.randn(5, 6), columns=("col %d" % i for i in range(6))
)

df2 = pd.DataFrame(
    np.random.randn(5, 6), columns=("col %d" % i for i in range(6))
)
my_chart = st.line_chart(df1)

# time.sleep(1)
my_chart.add_rows(df2)



# plotly
x1 = np.random.randn(200) - 2
x2 = np.random.randn(200)
x3 = np.random.randn(200) + 2

hist_data = [x1, x2, x3]
group_labels = ['Group 1', 'Group 2', 'Group 3']
fig = ff.create_distplot(
        hist_data, group_labels, bin_size=[.1, .25, .5])

st.plotly_chart(fig)

# sankey diagram


# pydeck
chart_data = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    columns=["lat", "lon"],
)

st.pydeck_chart(
    pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(
            latitude=37.76,
            longitude=-122.4,
            zoom=11,
            pitch=30,
        ),
        layers=[
            pdk.Layer(
                "HexagonLayer",
                data=chart_data,
                get_position="[lon, lat]",
                radius=200,
                elevation_scale=4,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
            ),
            pdk.Layer(
                "ScatterplotLayer",
                data=chart_data,
                get_position="[lon, lat]",
                get_color="[200, 30, 0, 160]",
                get_radius=200,
            ),
        ],
    )
)
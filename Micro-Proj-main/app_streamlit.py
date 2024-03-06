import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import time

while True:
    FASTAPI_ENDPOINT = "http://fastapi:8000/get_voltage_data/"

    response = requests.get(FASTAPI_ENDPOINT)
    data = response.json()

    df = pd.DataFrame(data)

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['power_watt'] = df['voltage'] * df['current']

    electricity_rate = 4
    df['electricity_cost'] = (df['power_watt'] * 1) / 1000 * electricity_rate

    st.write("ข้อมูลกระแสไฟ, แรงดันไฟ, ค่าพลังงาน, และค่าใช้จ่ายของไฟฟ้า (บาท):")
    st.dataframe(df)

    fig_amp = px.line(df, x='timestamp', y='current', title='กราฟแสดงกระแสไฟ')
    st.plotly_chart(fig_amp)

    fig_voltage = px.line(df, x='timestamp', y='voltage', title='กราฟแสดงแรงดันไฟ')
    st.plotly_chart(fig_voltage)

    fig_power = px.line(df, x='timestamp', y='power_watt', title='กราฟแสดงค่าพลังงาน')
    st.plotly_chart(fig_power)

    fig_cost = px.line(df, x='timestamp', y='electricity_cost', title='กราฟแสดงค่าใช้จ่ายของไฟฟ้า (บาท)')
    st.plotly_chart(fig_cost)

    time.sleep(5)
    st.experimental_rerun()

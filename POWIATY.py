import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# 1. Налаштування зовнішнього вигляду сторінки
st.set_page_config(layout="wide", page_title="Карта повітів")
st.title("Powiaty Polski")

# 2. Завантаження цифрових меж Польщі з інтернету
@st.cache_data
def load_geojson():
    url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/poland-powiats.geojson"
    return requests.get(url).json()

geojson_data = load_geojson()

# 3. Читання вашого Excel-файлу
try:
    df = pd.read_excel("data.xlsx")
    
    if 'poviat' in df.columns:
        all_poviats = sorted(df['poviat'].unique())
        
        # 4. Створення віконця пошуку повітів
        selected_poviats = st.multiselect(
            "Nazwa Powiat",
            options=all_poviats,
            default=[all_poviats[0]] if all_poviats else None
        )
        
        # 5. Логіка підсвічування: якщо повіт вибрано — статус один, якщо ні — інший
        df['status'] = df['poviat'].apply(lambda x: 'Шуканий повіт' if x in selected_poviats else 'Інші регіони')
        
        # 6. Малювання та налаштування інтерактивної карти
        fig = px.choropleth_mapbox(
            df,
            geojson=geojson_data,
            locations="poviat",
            featureidkey="properties.nazwa",
            color="status",
            color_discrete_map={"Шуканий повіт": "#EF4444", "Інші регіони": "#E2E8F0"},
            mapbox_style="carto-positron",
            zoom=5.6,
            center={"lat": 52.06, "lon": 19.47},
            opacity=0.75,
            hover_data=list(df.columns)
        )
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=600)
        
        # Відображення карти на екрані сайту
        st.plotly_chart(fig, use_container_width=True)
        
        # 7. Відображення таблиці з вашими даними під картою
        st.markdown("Informacja powiatu")
        filtered_df = df[df['poviat'].isin(selected_poviats)]
        st.dataframe(filtered_df.drop(columns=['status'], errors='ignore'), use_container_width=True)
    else:
        st.error("Помилка: В Excel немає колонки з назвою 'poviat'")
except FileNotFoundError:
    st.error("Помилка: Не знайдено файл 'data.xlsx' в папці сайту.")

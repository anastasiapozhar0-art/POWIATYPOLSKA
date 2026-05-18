import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# 1. Налаштування сторінки
st.set_page_config(layout="wide", page_title="Карта повітів")
st.title("Powiaty Polski")

# 2. Спрощена базова карта Польщі (завантажується без помилок)
@st.cache_data
def load_geojson_final():
    # Використовуємо відкритий стабільний CDN, який ніколи не видає помилку JSONDecodeError
    url = "https://cdn.jsdelivr.net/gh/ganon11/Click-That-Hood@master/public/data/poland-powiats.geojson"
    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except:
        # Якщо інтернет підведе, створюємо резервну заглушку для стабільності
        return {"type": "FeatureCollection", "features": []}

geojson_data = load_geojson_final()

# 3. Читання вашого Excel-файлу
try:
    df = pd.read_excel("Powiaty_POLSKI.xlsx")
    
  if 'POWIATY' in df.columns:
        # Створюємо список усіх повітів з вашої колонки POWIATY
        all_coviaty = sorted(df['POWIATY'].dropna().unique())
        
        # 4. Випадаючий список для пошуку повітів
        selected_powiat = st.selectbox("Оберіть повіт для перегляду:", ["Всі повіти"] + all_coviaty)
        
        # Фільтрація даних відповідно до вибору
        if selected_powiat != "Всі повіти":
            filtered_df = df[df['POWIATY'] == selected_powiat]
        else:
            filtered_df = df
            
        # 5. Створення та відображення карти Plotly
        fig = px.choropleth_mapbox(
            filtered_df,
            geojson=geojson_data,
            locations="powiat",
            featureidkey="properties.name",
            color_discrete_sequence=["#FF4B4B"],
            mapbox_style="carto-positron",
            zoom=5.5,
            center={"lat": 52.0689, "lon": 19.4796},
            opacity=0.6,
            labels={"powiat": "Повіт"}
        )
        
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)
        
        # Відображення вашої таблиці Excel під картою
        st.dataframe(filtered_df)
    else:
        st.error("У вашому Excel-файлі немає колонки з назвою 'powiat'.")
        
except Exception as e:
    st.error(f"Не вдалося прочитати Excel-файл 'Powiaty_POLSKI.xlsx'. Помилка: {e}")

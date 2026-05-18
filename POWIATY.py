import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# 1. Налаштування сторінки
st.set_page_config(layout="wide", page_title="Карта повітів")
st.title("🗺️ Контурна карта повітів Польщі")

# 2. Завантажуємо базову інтернет-карту
@st.cache_data
def load_geojson():
    url = "https://cdn.jsdelivr.net/gh/ganon11/Click-That-Hood@master/public/data/poland-powiats.geojson"
    try:
        data = requests.get(url, timeout=10).json()
        # Приводимо назви повітів у GEOJSON до нижнього регістру для ідеального збігу
        for feature in data.get("features", []):
            name = feature["properties"].get("name", "")
            feature["properties"]["name_clean"] = str(name).strip().lower()
        return data
    except:
        return {"type": "FeatureCollection", "features": []}

geojson_data = load_geojson()

# 3. Читання вашого Excel-файлу
try:
    df = pd.read_excel("Powiaty_POLSKI.xlsx")
    df.columns = [str(col).strip() for col in df.columns]
    
    if 'POWIATY' in df.columns:
        # Створюємо оригінальну колонку для відображення у списку (щоб користувач бачив гарні назви)
        df['POWIATY'] = df['POWIATY'].astype(str).str.strip()
        all_coviaty = sorted(df['POWIATY'].dropna().unique())
        
        # Створюємо СЛУЖБОВУ колонку для точного збігу з картою (очищаємо від "powiat" і робимо літери малими)
        df['POWIATY_MATCH'] = df['POWIATY'].str.replace(r'^[Pp]owiat\s+', '', regex=True).str.strip().str.lower()
        
        # Пошук повітів (Мультивибір за гарними назвами)
        selected_powiats = st.multiselect(
            "Введіть або оберіть повіти для підсвічування:", 
            options=all_coviaty,
            default=[]
        )

        # Створюємо базову чисту контурну карту (без написів міст)
        fig = px.choropleth_mapbox(
            df, 
            geojson=geojson_data,
            locations="POWIATY_MATCH",       # Шукаємо за очищеним службовим полем
            featureidkey="properties.name_clean", # Порівнюємо з очищеним полем карти
            mapbox_style="white-bg", 
            zoom=5.5,
            center={"lat": 52.0689, "lon": 19.4796},
            opacity=1.0
        )
        
        # Робимо фонову карту чисто білою з чіткими сірими контурами повітів
        fig.update_traces(
            marker_line_color="#7F7F7F", 
            marker_line_width=1, 
            colorscale=[[0, '#FFFFFF'], [1, '#FFFFFF']], 
            showscale=False
        )

        # Якщо ви вписали повіти в пошук — накладаємо їх зверху КОЛЬОРОМ
        if selected_powiats:
            filtered_df = df[df['POWIATY'].isin(selected_powiats)]
            
            colored_layer = px.choropleth_mapbox(
                filtered_df,
                geojson=geojson_data,
                locations="POWIATY_MATCH",
                featureidkey="properties.name_clean",
                color="POWIATY",
                color_discrete_sequence=px.colors.qualitative.Bold,
                opacity=0.9
            )
            
            # Додаємо кольорові шматочки на контурну карту
            for trace in colored_layer.data:
                fig.add_trace(trace)
        
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.error("У вашому Excel-файлі не знайдено колонку 'POWIATY'.")
except Exception as e:
    st.error(f"Помилка: {e}")

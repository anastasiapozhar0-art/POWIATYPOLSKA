import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# 1. Налаштування сторінки
st.set_page_config(layout="wide", page_title="Інтерактивна карта повітів")
st.title("🗺️ Мульти-карта повітів Польщі")

# 2. Завантаження карти Польщі (через стабільний CDN)
@st.cache_data
def load_geojson_final():
    url = "https://cdn.jsdelivr.net/gh/ganon11/Click-That-Hood@master/public/data/poland-powiats.geojson"
    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except:
        return {"type": "FeatureCollection", "features": []}

geojson_data = load_geojson_final()

# 3. Читання вашого Excel-файлу
try:
    df = pd.read_excel("Powiaty_POLSKI.xlsx")
    df.columns = [str(col).strip() for col in df.columns]
    
    if 'POWIATY' in df.columns:
        df['POWIATY'] = df['POWIATY'].astype(str).str.strip()
        all_coviaty = sorted(df['POWIATY'].dropna().unique())
        
        # Створюємо дві колонки для налаштувань та завантаження фото
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("✍️ Ручний вибір повітів")
            # МУЛЬТИВИБІР: тепер тут st.multiselect замість st.selectbox
            selected_powiats = st.multiselect(
                "Оберіть один або декілька повітів:", 
                options=all_coviaty,
                default=[]
            )
            
        with col2:
            st.subheader("📸 Автоматичний пошук з фото")
            uploaded_image = st.file_uploader("Завантажте фото зі списком повітів:", type=["png", "jpg", "jpeg"])
            
            if uploaded_image is not None:
                st.image(uploaded_image, caption="Завантажене фото", width=250)
                st.info("🔄 Функція сканування тексту підключається... Зачекайте на встановлення бібліотек.")
                
                # Тимчасова імітація пошуку (поки ви не підключите модуль розпізнавання тексту):
                # Тут буде логіка штучного інтелекту, яка прочитає фото і додасть повіти у список.

        # Фільтрація даних на основі обраних повітів
        if selected_powiats:
            filtered_df = df[df['POWIATY'].isin(selected_powiats)]
        else:
            filtered_df = df  # якщо нічого не обрано, показуємо все
            
        st.write(f"📊 Сортування активовано для повітів: {', '.join(selected_powiats) if selected_powiats else 'Всі'}")

        # 5. Створення карти з РІЗНИМИ кольорами (color="POWIATY")
        fig = px.choropleth_mapbox(
            filtered_df,
            geojson=geojson_data,
            locations="POWIATY",
            featureidkey="properties.name",
            color="POWIATY",  # Сама ця строчка фарбує кожен повіт в окремий колір!
            color_discrete_sequence=px.colors.qualitative.Bold, # Яскрава палітра кольорів
            mapbox_style="carto-positron",
            zoom=5.5,
            center={"lat": 52.0689, "lon": 19.4796},
            opacity=0.7,
            labels={"POWIATY": "Повіт"}
        )
        
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
        
        # Відображення таблиці
        st.dataframe(filtered_df)
    else:
        st.error("У вашому Excel-файлі не знайдено колонку 'POWIATY'. Перевірте назву стовпчика.")
        
except Exception as e:
    st.error(f"Не вдалося прочитати Excel-файл 'Powiaty_POLSKI.xlsx'. Помилка: {e}")

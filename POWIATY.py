import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests

# 1. Налаштування сторінки
st.set_page_config(layout="wide", page_title="Карта повітів")
st.title("🗺️ Контурна карта повітів Польщі")

# 2. Стабільне завантаження гео-контурів повітів Польщі
@st.cache_data
def load_geojson():
    url = "https://raw.githubusercontent.com/ganon11/Click-That-Hood/master/public/data/poland-powiats.geojson"
    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except Exception as e:
        st.error(f"Не вдалося завантажити контури карти: {e}")
        return None

geojson_data = load_geojson()

# 3. Читання вашого Excel-файлу
try:
    df = pd.read_excel("Powiaty_POLSKI.xlsx")
    df.columns = [str(col).strip() for col in df.columns]
    
    if 'POWIATY' in df.columns and geojson_data is not None:
        # Очищення назв в Excel від слова "powiat" для точного збігу з картою
        df['POWIATY_CLEAN'] = df['POWIATY'].astype(str).str.replace(r'^[Pp]owiat\s+', '', regex=True).str.strip().str.lower()
        
        # Список для гарного відображення в пошуку (оригінальні назви з Excel)
        all_powiats = sorted(df['POWIATY'].dropna().unique())
        
        # Віконце пошуку повітів (Мультивибір)
        selected_powiats = st.multiselect(
            "Введіть або оберіть повіти для підсвічування:", 
            options=all_powiats,
            default=[]
        )
        
        # Переводимо обрані користувачем повіти в очищений формат для порівняння з картою
        selected_clean = [str(p).replace("Powiat", "").replace("powiat", "").strip().lower() for p in selected_powiats]

        # 4. СТВОРЕННЯ БАЗОВОЇ КАРТИ
        # Центруємо карту на координатах Польщі
        m = folium.Map(location=[52.0689, 19.4796], zoom_start=6, tiles=None)
        
        # Робимо повністю чисте біле тло для карти (без міст, доріг та океанів)
        folium.TileLayer(
            tiles='https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png',
            attr='CartoDB',
            name='Чисте тло'
        ).add_to(m)

        # 5. ФУНКЦІЯ ФАРБУВАННЯ КОНТУРІВ
        # Ця функція перевіряє кожен повіт на карті: якщо він обраний в пошуку — робить кольоровим, якщо ні — білим із сірою межею
        def style_function(feature):
            name = feature['properties'].get('name', '').strip().lower()
            if name in selected_clean:
                # Кольорове підсвічування для обраних повітів (яскраво-червоний/малиновий колір)
                return {
                    'fillColor': '#FF2A6D',
                    'color': '#FF2A6D',
                    'weight': 2,
                    'fillOpacity': 0.7
                }
            else:
                # Базовий вигляд карти: білі повіти з чіткими сірими контурами
                return {
                    'fillColor': '#FFFFFF',
                    'color': '#7F7F7F',
                    'weight': 1,
                    'fillOpacity': 1.0
                }

        # Накладаємо контури повітрів на карту з нашою функцією стилю
        folium.GeoJson(
            geojson_data,
            style_function=style_function,
            tooltip=folium.GeoJsonTooltip(fields=['name'], aliases=['Повіт:'])
        ).add_to(m)

        # Відображаємо карту на сторінці Streamlit
        st_folium(m, width=1000, height=600, returned_objects=[])
        
    else:
        if 'POWIATY' not in df.columns:
            st.error("У вашому Excel-файлі не знайдено колонку 'POWIATY'.")
except Exception as e:
    st.error(f"Помилка виконання: {e}")

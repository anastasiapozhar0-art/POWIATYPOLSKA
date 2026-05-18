import streamlit as st
import pandas as pd
from PIL import Image
import os

# 1. Налаштування сторінки
st.set_page_config(layout="wide", page_title="Контурна карта")
st.title("🗺️ Комбінована контурна карта повітів Польщі")

# Назва вашої базової (чистої) карти-підкладки
BASE_MAP_PATH = "my_contour_map.png" 

# 2. Читання вашого Excel-файлу
try:
    df = pd.read_excel("Powiaty_POLSKI.xlsx")
    df.columns = [str(col).strip() for col in df.columns]
    
    if 'POWIATY' in df.columns:
        df['POWIATY'] = df['POWIATY'].astype(str).str.strip()
        all_powiats = sorted(df['POWIATY'].dropna().unique())
        
        # Віконце пошуку повітів (Мультивибір)
        selected_powiats = st.multiselect(
            "Введіть або оберіть повіти для підсвічування:", 
            options=all_powiats,
            default=[]
        )
        
        # 3. Логіка склеювання шарів
        if os.path.exists(BASE_MAP_PATH):
            base_image = Image.open(BASE_MAP_PATH).convert("RGBA")
            combined_image = base_image.copy()
            
            # Проходимо по кожному обраному в пошуку повіту
            for powiat_name in selected_powiats:
                # Перетворюємо назву: "Powiat Krakowski" -> "krakowski.png"
                # Замінюємо польські літери на звичайні, якщо ви так називали файли (наприклад, ó -> o, ł -> l)
                clean_name = powiat_name.replace("Powiat", "").replace("powiat", "").strip().lower()
                clean_name = clean_name.replace("ó", "o").replace("ł", "l").replace("ą", "a")
                clean_name = clean_name.replace("ę", "e").replace("ś", "s").replace("ź", "z")
                clean_name = clean_name.replace("ż", "z").replace("ć", "c").replace("ń", "n")
                
                # Прибираємо пробіли, якщо у назві два слова (наприклад, "dabrowski" чи "bielskobiala")
                clean_name = clean_name.replace(" ", "")
                
                powiat_file = f"{clean_name}.png"
                
                # Якщо картинка є — накладаємо її
                if os.path.exists(powiat_file):
                    powiat_image = Image.open(powiat_file).convert("RGBA")
                    combined_image = Image.alpha_composite(combined_image, powiat_image)
            
            # 4. Виводимо фінальну карту на екран
            st.image(combined_image, caption="Ваша інтерактивна контурна карта", use_column_width=True)
            
        else:
            st.error(f"Будь ласка, завантажте базову чисту карту на GitHub під назвою '{BASE_MAP_PATH}'")
            
    else:
        st.error("У вашому Excel-файлі не знайдено колонку 'POWIATY'.")
except Exception as e:
    st.error(f"Помилка роботи програми: {e}")

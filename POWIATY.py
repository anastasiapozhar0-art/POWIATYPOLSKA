import streamlit as st
import pandas as pd
from PIL import Image
import os

# 1. Налаштування сторінки
st.set_page_config(layout="wide", page_title="Контурна карта")
st.title("🗺️ Комбінована контурна карта повітів Польщі")

# Назва вашої базової карти-підкладки
BASE_MAP_PATH = "my_contour_map.png" 

# 2. Читання вашого Excel-файлу
try:
    df = pd.read_excel("Powiaty_POLSKI.xlsx")
    df.columns = [str(col).strip() for col in df.columns]
    
    if 'POWIATY' in df.columns:
        df['POWIATY'] = df['POWIATY'].astype(str).str.strip()
        all_powiats = sorted(df['POWIATY'].dropna().unique())
        
        # Віконце пошуку повітів
        selected_powiats = st.multiselect(
            "Введіть або оберіть повіти для підсвічування:", 
            options=all_powiats,
            default=[]
        )
        
        # 3. Логіка склеювання шарів (малюнок на малюнок)
        if os.path.exists(BASE_MAP_PATH):
            base_image = Image.open(BASE_MAP_PATH).convert("RGBA")
            combined_image = base_image.copy()
            
            # Проходимо по кожному обраному в пошуку повіту
            for powiat_name in selected_powiats:
                orig_name = powiat_name.strip() # Наприклад: "Powiat jasielski"
                
                # Чиста назва без слова "powiat": "jasielski"
                clean_name = orig_name.replace("Powiat", "").replace("powiat", "").strip()
                
                # Замінюємо польські літери на звичайні латинські
                def remove_polish_chars(text):
                    replacements = {'ó': 'o', 'ł': 'l', 'ą': 'a', 'ę': 'e', 'ś': 's', 'ź': 'z', 'ż': 'z', 'ć': 'c', 'ń': 'n',
                                    'Ó': 'O', 'Ł': 'L', 'Ą': 'A', 'Ę': 'E', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z', 'Ć': 'C', 'Ń': 'N'}
                    for src, dst in replacements.items():
                        text = text.replace(src, dst)
                    return text
                
                clean_lat = remove_polish_chars(clean_name)
                orig_lat = remove_polish_chars(orig_name)
                
                # Створюємо різні варіанти написання назв файлів (разом, через пробіл, через підкреслення)
                possible_filenames = [
                    f"{clean_lat.lower().replace(' ', '_')}.png",  # jasielski.png або такий варіант
                    f"powiat_{clean_lat.lower().replace(' ', '_')}.png",  # powiat_jasielski.png (Ваш варіант!)
                    f"{clean_lat.lower().replace(' ', '')}.png",   # jasielski.png
                    f"{orig_lat.lower().replace(' ', '')}.png",    # powiatjasielski.png
                    f"{orig_lat.lower().replace(' ', '_')}.png",   # powiat_jasielski.png
                    f"Powiat_{clean_lat.replace(' ', '_')}.png",   # Powiat_Jasielski.png
                    
                    # Те саме, тільки якщо розширення файлу великими літерами .PNG
                    f"powiat_{clean_lat.lower().replace(' ', '_')}.PNG",
                    f"{clean_lat.lower().replace(' ', '_')}.PNG"
                ]
                
                # Шукаємо, яка саме картинка збігається
                found_file = None
                for filename in possible_filenames:
                    if os.path.exists(filename):
                        found_file = filename
                        break
                
                # Якщо знайшли файл повіту — накладаємо його
                if found_file:
                    powiat_image = Image.open(found_file).convert("RGBA")
                    combined_image = Image.alpha_composite(combined_image, powiat_image)
            
            # 4. Виводимо готову карту на екран
            st.image(combined_image, caption="Ваша інтерактивна контурна карта", use_column_width=True)
            
        else:
            st.error(f"Будь ласка, завантажте базову чисту карту на GitHub під назвою '{BASE_MAP_PATH}'")
            
    else:
        st.error("У вашому Excel-файлі не знайдено колонку 'POWIATY'.")
except Exception as e:
    st.error(f"Помилка роботи програми: {e}")

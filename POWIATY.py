import streamlit as st
import pandas as pd
from PIL import Image
import os

st.set_page_config(layout="wide", page_title="Контурна карта повітів")
st.title("🗺️ Комбінована контурна карта повітів Польщі")

BASE_MAP_PATH = "my_contour_map.png" 

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
        
        if os.path.exists(BASE_MAP_PATH):
            base_image = Image.open(BASE_MAP_PATH).convert("RGBA")
            combined_image = base_image.copy()
            
            for powiat_name in selected_powiats:
                orig_name = powiat_name.strip()
                
                # Очищення назви під ваш формат "powiat_назва.png"
                clean_name = orig_name.lower().replace("powiat", "").strip().replace(" ", "")
                
                # Заміна польських літер
                def remove_polish_chars(text):
                    replacements = {'ó': 'o', 'ł': 'l', 'ą': 'a', 'ę': 'e', 'ś': 's', 'ź': 'z', 'ż': 'z', 'ć': 'c', 'ń': 'n'}
                    for src, dst in replacements.items():
                        text = text.replace(src, dst)
                    return text
                
                clean_lat = remove_polish_chars(clean_name)
                
                possible_filenames = [
                    f"powiat_{clean_lat}.png",
                    f"{clean_lat}.png",
                    f"powiat_{clean_lat}.PNG",
                    f"{clean_lat}.PNG"
                ]
                
                found_file = None
                for filename in possible_filenames:
                    if os.path.exists(filename):
                        found_file = filename
                        break
                
                if found_file:
                    powiat_image = Image.open(found_file).convert("RGBA")
                    
                    # --- МАГІЯ: Робимо чисто білий фон повністю прозорим ---
                    datas = powiat_image.getdata()
                    new_data = []
                    for item in datas:
                        # Якщо піксель білий (або майже білий), міняємо його на прозорий
                        if item[0] > 240 and item[1] > 240 and item[2] > 240:
                            new_data.append((255, 255, 255, 0)) # 0 - повна прозорість
                        else:
                            new_data.append(item)
                    powiat_image.putdata(new_data)
                    
                    # Накладаємо очищений повіт на карту
                    combined_image = Image.alpha_composite(combined_image, powiat_image)
            
            # Виводимо фінальну карту
            st.image(combined_image, caption="Ваша інтерактивна карта", use_column_width=True)
            
        else:
            st.error(f"Не знайдено базову карту під назвою '{BASE_MAP_PATH}'")
    else:
        st.error("У вашому Excel-файлі не знайдено колонку 'POWIATY'.")
except Exception as e:
    st.error(f"Помилка роботи програми: {e}")

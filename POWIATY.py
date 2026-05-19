import streamlit as st
import pandas as pd
from PIL import Image
import os

# Розумний сканер тексту
try:
    import easyocr
    import numpy as np
    reader = easyocr.Reader(['pl', 'en'], gpu=False)
except:
    reader = None

st.set_page_config(layout="wide", page_title="Розумна контурна карта")
st.title("📸 Смарт-карта повітів Польщі зі сканером")

BASE_MAP_PATH = "my_contour_map.png" 

try:
    df = pd.read_excel("Powiaty_POLSKI.xlsx")
    df.columns = [str(col).strip() for col in df.columns]
    
    if 'POWIATY' in df.columns:
        df['POWIATY'] = df['POWIATY'].astype(str).str.strip()
        all_powiats = sorted(df['POWIATY'].dropna().unique())
        
        # --- БЛОК СКАНЕРА ---
        st.subheader("🤖 Крок 1: Відскануйте текст з фото (опціонально)")
        uploaded_file = st.file_uploader("Натисніть, щоб зробити фото камери або завантажити картинку з телефона", type=["png", "jpg", "jpeg"])
        
        scanned_powiats = []
        if uploaded_file is not None:
            if reader is None:
                st.warning("🔄 Сканер налаштовується на сервері. Спробуйте ручний вибір нижче або зачекайте хвилину.")
            else:
                with st.spinner("🔍 Робот читає текст на фото..."):
                    img = Image.open(uploaded_file)
                    img_np = np.array(img)
                    results = reader.readtext(img_np, detail=0)
                    full_text = " ".join(results).lower().replace("-", "").replace("_", "")
                    
                    for p_name in all_powiats:
                        clean_p = p_name.lower().replace("powiat", "").strip().replace(" ", "").replace("-", "")
                        if clean_p in full_text and len(clean_p) > 3:
                            scanned_powiats.append(p_name)
                    
                    if scanned_powiats:
                        st.success(f"✅ Знайдено на фото повіти: {', '.join(scanned_powiats)}")
                    else:
                        st.info("ℹ️ Текст розпізнано, але назв повітів не знайдено.")

        # --- БЛОК ПОШУКУ ТА КАРТИ ---
        st.subheader("🗺️ Крок 2: Перегляд карти та ручний пошук")
        
        selected_powiats = st.multiselect(
            "Введіть або оберіть повіти для підсвічування:", 
            options=all_powiats,
            default=scanned_powiats
        )
        
        if os.path.exists(BASE_MAP_PATH):
            base_image = Image.open(BASE_MAP_PATH).convert("RGBA")
            combined_image = base_image.copy()
            
            for powiat_name in selected_powiats:
                orig_name = powiat_name.strip()
                
                # Стандартизація назви для пошуку файлу
                clean_name = orig_name.lower().replace("powiat", "").strip().replace(" ", "")
                
                def remove_polish_chars(text):
                    replacements = {'ó': 'o', 'ł': 'l', 'ą': 'a', 'ę': 'e', 'ś': 's', 'ź': 'z', 'ż': 'z', 'ć': 'c', 'ń': 'n'}
                    for src, dst in replacements.items():
                        text = text.replace(src, dst)
                    return text
                
                clean_lat = remove_polish_chars(clean_name)
                
                # Варіанти назв файлів (включаючи дефіси та підкреслення)
                possible_filenames = [
                    f"powiat_{clean_lat}.png",
                    f"powiat_{clean_lat.replace('-', '_')}.png",
                    f"powiat_{clean_lat.replace('-', '')}.png",
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
                    
                    # --- НОВА СУПЕР-МАГІЯ: Авто-хромакей фону ---
                    # Дізнаємося колір самого першого пікселя (це 100% фон)
                    bg_color = powiat_image.getpixel((0, 0))
                    
                    datas = powiat_image.getdata()
                    new_data = []
                    for item in datas:
                        # Якщо піксель схожий на колір фону АБО є білим — робимо його повністю прозорим
                        if (abs(item[0] - bg_color[0]) < 20 and abs(item[1] - bg_color[1]) < 20 and abs(item[2] - bg_color[2]) < 20) or (item[0] > 235 and item[1] > 235 and item[2] > 235):
                            new_data.append((255, 255, 255, 0))
                        else:
                            new_data.append(item)
                    powiat_image.putdata(new_data)
                    
                    # Накладання шару
                    combined_image = Image.alpha_composite(combined_image, powiat_image)
            
            st.image(combined_image, caption="Ваша оновлена розумна карта", use_column_width=True)
        else:
            st.error(f"Не знайдено базову карту під назвою '{BASE_MAP_PATH}'")
            
except Exception as e:
    st.error(f"Помилка: {e}")

import streamlit as st
import pandas as pd
from PIL import Image
import os

# Спробуємо підключити сканер тексту. Якщо сервер ще вантажить його - сайт не впаде
try:
    import easyocr
    import numpy as np
    reader = easyocr.Reader(['pl', 'en'], gpu=False) # Польська та англійська мови
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
        
        # --- БЛОК СКАНЕРА З ФОТО ---
        st.subheader("🤖 Крок 1: Відскануйте текст з фото (опціонально)")
        uploaded_file = st.file_uploader("Натисніть, щоб зробити фото камери або завантажити картинку з телефона", type=["png", "jpg", "jpeg"])
        
        scanned_powiats = []
        if uploaded_file is not None:
            if reader is None:
                st.warning("🔄 Робот-сканер ще налаштовується на сервері. Будь ласка, зачекайте хвилину або виберіть повіти вручну нижче.")
            else:
                with st.spinner("🔍 Робот читає текст на фото... зачекайте секунду..."):
                    img = Image.open(uploaded_file)
                    img_np = np.array(img)
                    # Зчитуємо весь текст з картинки
                    results = reader.readtext(img_np, detail=0)
                    full_text = " ".join(results).lower()
                    
                    # Шукаємо, які повіти з нашого Excel згадуються в тексті на фото
                    for p_name in all_powiats:
                        clean_p = p_name.replace("Powiat", "").replace("powiat", "").strip().lower()
                        if clean_p in full_text and len(clean_p) > 3:
                            scanned_powiats.append(p_name)
                    
                    if scanned_powiats:
                        st.success(f"✅ Знайдено на фото повіти: {', '.join(scanned_powiats)}")
                    else:
                        st.info("ℹ️ Текст розпізнано, але назв повітів з вашого Excel там не знайдено.")

        # --- БЛОК ПОШУКУ ТА КАРТИ ---
        st.subheader("🗺️ Крок 2: Перегляд карти та ручний пошук")
        
        # Об'єднуємо повіти з фото та ті, що ви можете додати ручним пошуком
        selected_powiats = st.multiselect(
            "Тут відображаються повіти (ви можете додати інші вручну):", 
            options=all_powiats,
            default=scanned_powiats
        )
        
        # Логіка склеювання шарів картинок
        if os.path.exists(BASE_MAP_PATH):
            base_image = Image.open(BASE_MAP_PATH).convert("RGBA")
            combined_image = base_image.copy()
            
            for powiat_name in selected_powiats:
                orig_name = powiat_name.strip()
                
                # Очищення назви (прибираємо пробіли, робимо маленькими)
                clean_name = orig_name.lower().replace("powiat", "").strip().replace(" ", "")
                
                # Замінюємо польські літери на звичайні
                def remove_polish_chars(text):
                    replacements = {'ó': 'o', 'ł': 'l', 'ą': 'a', 'ę': 'e', 'ś': 's', 'ź': 'z', 'ż': 'z', 'ć': 'c', 'ń': 'n',
                                    'Ó': 'O', 'Ł': 'L', 'Ą': 'A', 'Ę': 'E', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z', 'Ć': 'C', 'Ń': 'N'}
                    for src, dst in replacements.items():
                        text = text.replace(src, dst)
                    return text
                
                clean_lat = remove_polish_chars(clean_name)
                orig_lat = remove_polish_chars(orig_name)
                
                # Створюємо різні варіанти написання назв файлів (з підкресленням, без, як було раніше)
                possible_filenames = [
                    f"powiat_{clean_lat}.png",        # powiat_jasielski.png
                    f"{clean_lat}.png",                # jasielski.png
                    f"powiat_{orig_lat.lower().replace(' ', '_')}.png",
                    f"{clean_lat}.PNG",
                    f"powiat_{clean_lat}.PNG"
                ]
                
                # Шукаємо, яка саме картинка лежить на GitHub
                found_file = None
                for filename in possible_filenames:
                    if os.path.exists(filename):
                        found_file = filename
                        break
                
                if found_file:
                    powiat_image = Image.open(found_file).convert("RGBA")
                    
                    # --- МАГІЯ: Вирізаємо білий фон кодом ---
                    datas = powiat_image.getdata()
                    new_data = []
                    for item in datas:
                        # Якщо піксель чисто білий (R, G, B = 255), робимо його прозорим (Alpha = 0)
                        # Іноді білий не ідеальний, тож ставимо поріг 240
                        if item[0] > 240 and item[1] > 240 and item[2] > 240:
                            new_data.append((255, 255, 255, 0)) # Робимо прозорим
                        else:
                            new_data.append(item)
                    powiat_image.putdata(new_data)
                    
                    # Накладаємо очищений повіт на карту
                    combined_image = Image.alpha_composite(combined_image, powiat_image)
            
            st.image(combined_image, caption="Ваша оновлена карта", use_column_width=True)
        else:
            st.error(f"Завантажте чисту карту під назвою '{BASE_MAP_PATH}'")
            
except Exception as e:
    st.error(f"Помилка: {e}")

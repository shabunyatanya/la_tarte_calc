import streamlit as st
import pandas as pd
from fpdf import FPDF
import io

st.set_page_config(page_title="La Tarte - online калькулятор", layout="wide")
st.title("La Tarte - online калькулятор")

# --- Ввод диаметров ---
col1, col2 = st.columns(2)
with col1:
    d_original = st.number_input("Исходный диаметр тарта (см):", min_value=1.0, value=7.0)
with col2:
    d_new = st.number_input("Новый диаметр тарта (см):", min_value=1.0, value=22.0)

st.markdown("---")

# --- Загрузка файла рецепта ---
uploaded_file = st.file_uploader(
    "Загрузите рецепт (png, jpg, jpeg, doc, pdf)",
    type=["png", "jpg", "jpeg", "doc", "pdf"]
)
if uploaded_file:
    if uploaded_file.type.startswith("image/"):
        st.image(uploaded_file, caption="Ваше фото", use_column_width=True)
    else:
        st.write("Файл загружен (для DOC/PDF/текста пока используется как справка).")

st.markdown("---")

# --- Ввод рецепта текстом ---
st.subheader("Введите рецепт вручную")
recipe_text = st.text_area(
    "Формат: ингредиент, количество, единица (например: мука, 300, г)",
    height=150
)

# --- Кнопка расчета ---
if st.button("Рассчитать рецепт"):
    if not recipe_text.strip():
        st.warning("Сначала введите рецепт текстом или загрузите файл.")
    else:
        # --- Преобразуем текст в DataFrame ---
        lines = [line.strip() for line in recipe_text.strip().split("\n") if line.strip()]
        data = []
        for line in lines:
            try:
                parts = [x.strip() for x in line.split(",")]
                if len(parts) != 3:
                    st.error(f"Неправильный формат строки: {line}")
                    continue
                name, qty, unit = parts
                data.append([name, float(qty), unit])
            except:
                st.error(f"Ошибка при разборе строки: {line}")
        df = pd.DataFrame(data, columns=["Название", "Количество", "Единица"])
        
        # --- Пересчет количества ---
        scale = (d_new / d_original) ** 2
        df["Количество"] = df["Количество"] * scale
        st.write(f"Коэффициент увеличения: {scale:.2f}x")
        st.table(df)

        # --- Генерация PDF ---
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "La Tarte – пересчитанный рецепт", ln=True, align='C')
        pdf.set_font("Arial", '', 12)
        pdf.ln(5)
        pdf.cell(0, 10, f"Исходный диаметр: {d_original} см", ln=True)
        pdf.cell(0, 10, f"Новый диаметр: {d_new} см", ln=True)
        pdf.ln(5)
        pdf.cell(0, 10, "Ингредиенты:", ln=True)
        pdf.ln(2)
        for i, row in df.iterrows():
            pdf.cell(0, 8, f"{row['Название']}: {row['Количество']:.1f} {row['Единица']}", ln=True)

        pdf_buffer = io.BytesIO()
        pdf.output(pdf_buffer)
        pdf_buffer.seek(0)

        st.download_button(
            label="Скачать рецепт в PDF",
            data=pdf_buffer,
            file_name="la_tarte_recipe.pdf",
            mime="application/pdf"
        )

import streamlit as st
import pandas as pd
from fpdf import FPDF
import io

st.set_page_config(page_title="La Tarte 🍰", layout="wide")
st.title("La Tarte – калькулятор рецептов тарталеток")

# Ввод исходного и нового диаметра
col1, col2 = st.columns(2)
with col1:
    d_original = st.number_input("Исходный диаметр тарта (см):", min_value=1.0, value=7.0)
with col2:
    d_new = st.number_input("Новый диаметр тарта (см):", min_value=1.0, value=22.0)

# Загрузка фото рецепта (для справки)
uploaded_file = st.file_uploader("Загрузите фото рецепта или ингредиентов", type=["png", "jpg", "jpeg"])
if uploaded_file is not None:
    st.image(uploaded_file, caption="Ваше фото", use_column_width=True)

# DataFrame для ингредиентов
if "ingredients" not in st.session_state:
    st.session_state.ingredients = pd.DataFrame(columns=["Название", "Количество", "Единица"])

st.subheader("Ингредиенты")
df = st.session_state.ingredients

# Форма для добавления нового ингредиента
with st.form("add_ingredient"):
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("Название ингредиента")
    with col2:
        qty = st.number_input("Количество", min_value=0.0, value=0.0)
    with col3:
        unit = st.text_input("Единица", value="г")
    submitted = st.form_submit_button("Добавить ингредиент")
    if submitted and name:
        st.session_state.ingredients = pd.concat([st.session_state.ingredients,
                                                  pd.DataFrame([[name, qty, unit]], columns=["Название", "Количество", "Единица"])],
                                                 ignore_index=True)
        st.experimental_rerun()

# Показываем таблицу
st.table(st.session_state.ingredients)

# Расчёт и генерация PDF
if st.button("Рассчитать рецепт для нового диаметра"):
    if df.empty:
        st.warning("Сначала добавьте ингредиенты!")
    else:
        scale = (d_new / d_original) ** 2
        st.write(f"Коэффициент увеличения: {scale:.2f}x")
        df_new = df.copy()
        df_new["Количество"] = df_new["Количество"] * scale
        st.write(df_new)

        # Создаём PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "La Tarte – рецепт", ln=True, align='C')
        pdf.set_font("Arial", '', 12)
        pdf.ln(5)
        pdf.cell(0, 10, f"Исходный диаметр: {d_original} см", ln=True)
        pdf.cell(0, 10, f"Новый диаметр: {d_new} см", ln=True)
        pdf.ln(5)
        pdf.cell(0, 10, "Ингредиенты:", ln=True)
        pdf.ln(2)

        for i, row in df_new.iterrows():
            pdf.cell(0, 8, f"{row['Название']}: {row['Количество']:.1f} {row['Единица']}", ln=True)

        # Сохраняем PDF в поток
        pdf_buffer = io.BytesIO()
        pdf.output(pdf_buffer)
        pdf_buffer.seek(0)

        st.download_button(
            label="Скачать рецепт в PDF",
            data=pdf_buffer,
            file_name="la_tarte_recipe.pdf",
            mime="application/pdf"
        )

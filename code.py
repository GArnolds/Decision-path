import streamlit as st

st.set_page_config(page_title="Ruta de decisión estadística", layout="centered")

st.title("🧠 Ruta interactiva: ¿Qué prueba estadística debo usar?")
st.write("Responde las preguntas y te guiaré a la prueba correcta.")

st.write("---")

# -----------------------------
# PREGUNTA 1: TIPO DE ANÁLISIS
# -----------------------------
q1 = st.radio(
    "1️⃣ ¿Qué quieres analizar?",
    [
        "Comparar grupos",
        "Asociar variables",
        "Predicción (regresión)"
    ]
)

st.write("---")

# =====================================================
#               COMPARAR GRUPOS
# =====================================================
if q1 == "Comparar grupos":

    # Número de grupos
    n_groups = st.radio(
        "2️⃣ ¿Cuántos grupos quieres comparar?",
        ["2 grupos", "Más de 2 grupos"]
    )

    # Independencia
    independent = st.radio(
        "3️⃣ ¿Las muestras son independientes o relacionadas?",
        ["Independientes", "Relacionadas / Pareadas"]
    )

    # Normalidad
    normal = st.radio(
        "4️⃣ ¿Los datos siguen una distribución normal?",
        ["Sí", "No"]
    )

    st.write("---")

    # -------------------------
    # RESULTADOS
    # -------------------------
    st.subheader("📌 Prueba recomendada")

    # 2 GRUPOS
    if n_groups == "2 grupos":

        if independent == "Independientes":

            if normal == "Sí":
                st.success("### t de Student para muestras independientes")
                st.write("""
                **Cuándo usarla:**  
                - Comparas medias de 2 grupos independientes  
                - Los datos son normales  
                - Varianzas similares  
                """)

            else:
                st.success("### U de Mann–Whitney")
                st.write("""
                **Cuándo usarla:**  
                - 2 grupos independientes  
                - Datos no normales u ordinales  
                """)

        # Relacionadas
        else:
            if normal == "Sí":
                st.success("### t de Student para muestras relacionadas")
                st.write("""
                **Cuándo usarla:**  
                - Muestras pareadas  
                - Medición antes–después  
                - Diferencias normales  
                """)

            else:
                st.success("### Prueba de Wilcoxon")
                st.write("""
                **Cuándo usarla:**  
                - Datos pareados  
                - No normales  
                """)

    # MÁS DE 2 GRUPOS
    elif n_groups == "Más de 2 grupos":

        if normal == "Sí" and independent == "Independientes":
            st.success("### ANOVA de un factor")
            st.write("""
            **Cuándo usarla:**  
            - 3 o más grupos independientes  
            - Datos normales  
            - Varianzas homogéneas  
            """)

        else:
            st.success("### Kruskal–Wallis")
            st.write("""
            **Cuándo usarla:**  
            - 3 o más grupos independientes  
            - Datos NO normales  
            - Datos ordinales o muestras pequeñas  
            """)

# =====================================================
#             ASOCIAR VARIABLES (CORRELACIÓN)
# =====================================================
elif q1 == "Asociar variables":

    tipo_var = st.radio(
        "2️⃣ ¿Qué tipo de variables quieres relacionar?",
        [
            "Dos variables numéricas",
            "Dos variables categóricas",
            "Una numérica y una categórica"
        ]
    )

    st.write("---")

    st.subheader("📌 Prueba recomendada")

    # NUMÉRICAS
    if tipo_var == "Dos variables numéricas":

        normal_corr = st.radio(
            "¿Ambas variables siguen distribución normal?",
            ["Sí", "No"]
        )

        if normal_corr == "Sí":
            st.success("### Correlación de Pearson")
            st.write("""
            **Cuándo usarla:**  
            - Dos variables numéricas  
            - Relación lineal  
            - Normalidad  
            """)

        else:
            st.success("### Correlación de Spearman")
            st.write("""
            **Cuándo usarla:**  
            - Variables numéricas NO normales  
            - Variables ordinales  
            - Relación monotónica  
            """)

    # CATEGÓRICAS
    elif tipo_var == "Dos variables categóricas":
        st.success("### Chi-cuadrada de independencia")
        st.write("""
        **Cuándo usarla:**  
        - Dos variables categóricas  
        - Tabla de contingencia  
        - Frecuencias esperadas ≥ 5  
        """)

    # NUMÉRICA + CATEGÓRICA
    elif tipo_var == "Una numérica y una categórica":
        st.info("""
        ➡️ Esto no es una correlación, sino una **comparación de medias entre grupos**.

        Usa:  
        - **t de Student / Mann–Whitney** si hay 2 grupos  
        - **ANOVA / Kruskal–Wallis** si hay más de 2 grupos  
        """)

# =====================================================
#                    REGRESIÓN
# =====================================================
elif q1 == "Predicción (regresión)":

    st.subheader("📌 Prueba recomendada")

    st.success("### Regresión lineal simple")
    st.write("""
    **Cuándo usarla:**  
    - Una variable independiente (predictora)  
    - Una variable dependiente numérica  
    - Relación lineal  
    """)

st.write("---")
st.write("Hecho con ❤️ para ayudarte a elegir la prueba correcta.")

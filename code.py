import streamlit as st

st.set_page_config(page_title="Árbol de decisión estadístico", layout="centered")

st.title("Árbol de decisión para elegir una prueba estadística")

st.write("Responde las preguntas y el sistema te dirá cuál prueba usar.")

# --- Pregunta 1 ---
q1 = st.radio(
    "1. ¿Tu variable dependiente es numérica o categórica?",
    ["Numérica", "Categórica"],
    index=None
)

if q1 == "Numérica":
    # --- Pregunta 2 ---
    q2 = st.radio(
        "2. ¿Tus datos siguen una distribución normal?",
        ["Sí", "No"],
        index=None
    )

    if q2:
        # --- Pregunta 3 ---
        q3 = st.radio(
            "3. ¿Estás comparando 2 grupos o más de 2 grupos?",
            ["2 grupos", "Más de 2 grupos"],
            index=None
        )

        if q3 == "2 grupos":
            # --- Pregunta 4 ---
            q4 = st.radio(
                "4. ¿Los grupos son independientes o relacionados?",
                ["Independientes", "Relacionados"],
                index=None
            )

            if q4 and q2 == "Sí":
                if q4 == "Independientes":
                    st.success("👉 **Prueba recomendada: t de Student para muestras independientes**")
                else:
                    st.success("👉 **Prueba recomendada: t de Student para muestras relacionadas (pareada)**")

            if q4 and q2 == "No":
                if q4 == "Independientes":
                    st.success("👉 **Prueba recomendada: U de Mann–Whitney**")
                else:
                    st.success("👉 **Prueba recomendada: Prueba de Wilcoxon**")

        if q3 == "Más de 2 grupos":
            if q2 == "Sí":
                st.success("👉 **Prueba recomendada: ANOVA de un factor**")
            else:
                st.success("👉 **Prueba recomendada: Kruskal–Wallis**")


# ---------------- CATEGÓRICAS ----------------

if q1 == "Categórica":
    q5 = st.radio(
        "2. ¿Quieres analizar asociación/relación entre variables categóricas?",
        ["Sí", "No"],
        index=None
    )

    if q5 == "Sí":
        st.success("👉 **Prueba recomendada: Chi-cuadrada**")

    if q5 == "No":
        q6 = st.radio(
            "3. ¿Quieres analizar asociación entre variables numéricas y categóricas?",
            ["Sí", "No"],
            index=None
        )

        if q6 == "Sí":
            q7 = st.radio(
                "4. ¿Tu variable numérica sigue una distribución normal?",
                ["Sí", "No"],
                index=None
            )

            if q7 == "Sí":
                st.success("👉 **Prueba recomendada: Correlación de Pearson**")
            elif q7 == "No":
                st.success("👉 **Prueba recomendada: Correlación de Spearman**")

        if q6 == "No":
            st.warning("⚠ No hay suficiente información para determinar una prueba.")

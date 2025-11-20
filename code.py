import streamlit as st
from graphviz import Digraph

st.set_page_config(page_title="Ruta de decisión estadística", layout="wide")

# Título
st.title("🧠 Ruta de decisión: ¿Qué prueba estadística debo usar?")
st.write("Este diagrama muestra un camino lógico para elegir la prueba adecuada según tu tipo de variable, comparación y supuestos.")

# Crear diagrama
g = Digraph("decision_tree", format="png")
g.attr(rankdir="LR", size="10,5")

# Nodos principales
g.node("A", "¿Qué quieres analizar?")
g.node("B1", "Comparar grupos")
g.node("B2", "Asociar variables")
g.edge("A", "B1")
g.edge("A", "B2")

# --- Comparar grupos ---
g.node("C1", "¿Cuántos grupos?")
g.edge("B1", "C1")

# 2 grupos
g.node("D1", "2 grupos")
g.edge("C1", "D1")

g.node("E1", "¿Las muestras son independientes?")
g.edge("D1", "E1")

# Independientes
g.node("F1", "Independientes")
g.edge("E1", "F1")

g.node("G1", "¿Datos normales?")
g.edge("F1", "G1")

g.node("H1", "t de Student (muestras independientes)")
g.node("H2", "U de Mann-Whitney")
g.edge("G1", "H1", label="Sí")
g.edge("G1", "H2", label="No")

# Relacionadas
g.node("F2", "Relacionadas / Pareadas")
g.edge("E1", "F2")

g.node("G2", "¿Datos normales?")
g.edge("F2", "G2")

g.node("H3", "t de Student (muestras relacionadas)")
g.node("H4", "Wilcoxon")
g.edge("G2", "H3", label="Sí")
g.edge("G2", "H4", label="No")

# Más de 2 grupos
g.node("D2", "Más de 2 grupos")
g.edge("C1", "D2")

g.node("E2", "¿Datos normales y varianzas iguales?")
g.edge("D2", "E2")

g.node("H5", "ANOVA de un factor")
g.node("H6", "Kruskal-Wallis")
g.edge("E2", "H5", label="Sí")
g.edge("E2", "H6", label="No")

# --- Asociar variables ---
g.node("C2", "¿Tipo de variables?")
g.edge("B2", "C2")

g.node("D3", "Dos variables numéricas")
g.node("D4", "Categórica vs Categórica")
g.edge("C2", "D3")
g.edge("C2", "D4")

# Correlaciones
g.node("E3", "¿Distribución normal?")
g.edge("D3", "E3")

g.node("H7", "Correlación de Pearson")
g.node("H8", "Correlación de Spearman")
g.edge("E3", "H7", label="Sí")
g.edge("E3", "H8", label="No")

# Chi-cuadrada
g.node("H9", "Chi-cuadrada de independencia")
g.edge("D4", "H9")

# Regresión
g.node("D5", "Asociación numérica con predicción")
g.edge("B2", "D5")

g.node("H10", "Regresión lineal simple")
g.edge("D5", "H10")

# Renderizar en Streamlit
st.graphviz_chart(g)

st.write("---")
st.subheader("📌 Pruebas incluidas")
st.write("""
- t de Student para muestras independientes
- U de Mann–Whitney
- Chi-cuadrada
- t de Student para muestras relacionadas
- Wilcoxon
- ANOVA de un factor
- Kruskal–Wallis
- Correlación de Pearson
- Correlación de Spearman
- Regresión lineal simple
""")

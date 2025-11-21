# app.py
import streamlit as st
from textwrap import dedent

st.set_page_config(page_title="Ruta interactiva: elegir prueba estadística", layout="wide")

# ---------- Datos de referencia (tabla completada) ----------
# Mapa con la información de cada prueba: objetivo, supuestos mínimos y descripción corta
PRUEBAS = {
    "t_independientes": {
        "nombre": "t de Student (muestras independientes)",
        "param": "Paramétrica",
        "objetivo": "Comparar medias entre dos grupos independientes.",
        "supuestos": [
            "Grupos independientes",
            "Ambos grupos aproximadamente normales",
            "Varianzas homogéneas",
            "Al menos 15 observaciones por grupo (recomendado)"
        ],
        "nota": "Usar si se cumplen los supuestos; si la normalidad falla o n pequeño -> Mann–Whitney."
    },
    "mann_whitney": {
        "nombre": "U de Mann–Whitney",
        "param": "No paramétrica",
        "objetivo": "Comparar dos grupos independientes cuando los datos son ordinales o no normales.",
        "supuestos": [
            "Grupos independientes",
            "Datos ordinales o continuos con distribución asimétrica",
            "Al menos 5-10 observaciones por grupo (recomendado)"
        ],
        "nota": "Alternativa a t independiente cuando no se cumplen supuestos paramétricos."
    },
    "t_pareado": {
        "nombre": "t de Student (muestras relacionadas / pareadas)",
        "param": "Paramétrica",
        "objetivo": "Comparar medias de dos mediciones emparejadas (mismos sujetos).",
        "supuestos": [
            "Diferencias entre pares aproximadamente normales",
            "Mediciones continuas en los mismos sujetos",
            "Al menos 30 pares (recomendado)"
        ],
        "nota": "Si las diferencias no son normales, usar Wilcoxon."
    },
    "wilcoxon": {
        "nombre": "Prueba de Wilcoxon (para pares)",
        "param": "No paramétrica",
        "objetivo": "Comparar dos muestras relacionadas cuando no se cumple normalidad.",
        "supuestos": [
            "Datos pareados o dependientes",
            "Escala al menos ordinal",
            "Al menos ~10 pares (recomendado)"
        ],
        "nota": "Alternativa pareada no paramétrica a la t pareada."
    },
    "anova": {
        "nombre": "ANOVA de un factor",
        "param": "Paramétrica",
        "objetivo": "Comparar medias de más de dos grupos independientes.",
        "supuestos": [
            "Normalidad aproximada en cada grupo",
            "Homogeneidad de varianzas (Levene)",
            "Grupos independientes",
            "Al menos 30 observaciones por grupo (recomendado)"
        ],
        "nota": "Si la normalidad/varianzas no se cumplen -> Kruskal–Wallis."
    },
    "kruskal": {
        "nombre": "Kruskal–Wallis",
        "param": "No paramétrica",
        "objetivo": "Comparar más de dos grupos independientes cuando no hay normalidad.",
        "supuestos": [
            "Grupos independientes",
            "Datos al menos ordinales",
            "No requiere normalidad",
            "Al menos 5 observaciones por grupo (recomendado)"
        ],
        "nota": "Alternativa no paramétrica al ANOVA."
    },
    "pearson": {
        "nombre": "Correlación de Pearson",
        "param": "Paramétrica",
        "objetivo": "Medir relación lineal entre dos variables numéricas.",
        "supuestos": [
            "Ambas variables numéricas",
            "Ambas aproximadamente normales",
            "Relación lineal",
            "Al menos 30 observaciones (recomendado)"
        ],
        "nota": "Mide fuerza y dirección de relación lineal."
    },
    "spearman": {
        "nombre": "Correlación de Spearman",
        "param": "No paramétrica",
        "objetivo": "Medir relación monotónica entre variables (ordinales o no normales).",
        "supuestos": [
            "Variables ordinales o numéricas no normales",
            "Relacion monotónica (no necesariamente lineal)",
            "Adecuada si hay valores extremos"
        ],
        "nota": "Se calcula sobre rangos; alternativa cuando no se cumple Pearson."
    },
    "chi2": {
        "nombre": "Chi-cuadrada de independencia",
        "param": "No paramétrica",
        "objetivo": "Examinar asociación entre variables categóricas.",
        "supuestos": [
            "Variables categóricas",
            "Al menos 80% de celdas con frecuencia esperada >= 5 (si no, agrupar)",
            "Muestra suficientemente grande (comúnmente >= 20)"
        ],
        "nota": "Si muchas celdas tienen esperadas <5, considerar Fisher o agrupar."
    },
    "regresion": {
        "nombre": "Regresión lineal simple",
        "param": "Paramétrica",
        "objetivo": "Predecir una variable dependiente continua a partir de una independiente.",
        "supuestos": [
            "Relación lineal entre variables",
            "Independencia de residuos",
            "Homocedasticidad (varianza constante de residuos)",
            "Normalidad de residuos",
            "Una sola variable independiente"
        ],
        "nota": "Si hay múltiples predictores usar regresión lineal múltiple."
    }
}

# ---------- Helpers ----------
def show_prueba_result(key, checks: dict):
    """Muestra resultado formateado con verificación de supuestos/tamaños."""
    p = PRUEBAS[key]
    st.success(f"🔎 Recomendación: **{p['nombre']}**")
    st.markdown(f"**Tipo:** {p['param']}")
    st.markdown(f"**Objetivo:** {p['objetivo']}")
    st.markdown("**Descripción breve:**")
    st.write(p.get("nota", ""))
    st.markdown("**Supuestos / criterios (tabla de referencia):**")
    for s in p["supuestos"]:
        st.write(f"- {s}")

    # Verificación automática simple: checks contiene flags (bool) y tamaños
    st.markdown("**Comprobaciones automáticas (según tus respuestas / tamaños ingresados):**")
    issues = []
    for k, v in checks.items():
        # present check details nicely
        if isinstance(v, tuple):
            label, ok = v
        else:
            label, ok = k, v
        if ok:
            st.write(f"✅ {label}")
        else:
            st.write(f"⚠️ {label}")
            issues.append(label)
    if issues:
        st.warning("Atención: algunas condiciones recomendadas no se cumplen. Revisa la nota y considera la prueba alternativa.")
    else:
        st.info("Todos los criterios recomendados (según tus entradas) se cumplen.")

# ---------- UI ----------
st.title("🧠 Ruta interactiva: ¿Qué prueba estadística debo usar?")
st.write(dedent("""
    Esta herramienta te guía paso a paso. Responde las preguntas (algunas opciones permiten ingresar tamaños de muestra).
    Al final recibirás: **nombre de la prueba + criterios + comprobación automática** (si los supuestos/tamaños mínimos que ingresaste cumplen las recomendaciones).
"""))

# Step 1: ¿Qué quieres hacer?
choice = st.radio("1) ¿Qué quieres hacer?", ["Comparar grupos", "Asociar variables", "Predicción (Regresión lineal simple)"])

# ---------- Comparar grupos ----------
if choice == "Comparar grupos":
    n_groups = st.radio("2) ¿Cuántos grupos vas a comparar?", ["2 grupos", "Más de 2 grupos"])
    if n_groups == "2 grupos":
        indep = st.radio("3) ¿Las muestras son independientes?", ["Sí (independientes)", "No (pareadas / relacionadas)"])
        if indep.startswith("Sí"):
            # Independent two groups flow
            st.markdown("**Comparación entre 2 grupos independientes**")
            # Ask about normality and homogeneity
            normal = st.radio("4) ¿Los datos en ambos grupos siguen una distribución aproximadamente normal?", ["Sí", "No", "No sé / No lo sé"])
            if normal == "Sí":
                hom = st.radio("5) ¿Las varianzas de ambos grupos son aproximadamente iguales (homogeneidad)?", ["Sí", "No", "No sé / No lo sé"])
                # Ask for sample sizes (optional)
                col1, col2 = st.columns(2)
                with col1:
                    n1 = st.number_input("Tamaño grupo 1 (n1) — opcional", min_value=0, step=1, value=0)
                with col2:
                    n2 = st.number_input("Tamaño grupo 2 (n2) — opcional", min_value=0, step=1, value=0)

                # Decision: prefer t if normal and homogeneity ok, else suggest check
                if normal == "Sí" and hom == "Sí":
                    # Check sample sizes
                    checks = {}
                    checks["Grupos independientes"] = True
                    checks["Normalidad en ambos grupos"] = True
                    checks["Varianzas homogéneas"] = True
                    # sample size recommended >=15 per group
                    if n1 >= 15 and n2 >= 15:
                        checks["n >= 15 por grupo"] = True
                    else:
                        checks["n >= 15 por grupo"] = (f"{n1} y {n2}", False) if (n1>0 or n2>0) else ("Tamaño no especificado", False)
                    show_prueba_result("t_independientes", checks)
                else:
                    # Not comfortable with parametric assumptions -> Mann-Whitney
                    checks = {}
                    checks["Grupos independientes"] = True
                    checks["Normalidad en ambos grupos"] = ( "No", False ) if normal == "No" else ("No seguro", False)
                    # Check minimal sample sizes for Mann-Whitney
                    if n1 >= 5 and n2 >= 5:
                        checks["n >= 5 por grupo"] = True
                    else:
                        checks["n >= 5 por grupo"] = (f"{n1} y {n2}", False) if (n1>0 or n2>0) else ("Tamaño no especificado", False)
                    show_prueba_result("mann_whitney", checks)

            elif normal == "No":
                # Non-normal -> Mann-Whitney
                col1, col2 = st.columns(2)
                with col1:
                    n1 = st.number_input("Tamaño grupo 1 (n1) — opcional", min_value=0, step=1, value=0, key="n1_mw")
                with col2:
                    n2 = st.number_input("Tamaño grupo 2 (n2) — opcional", min_value=0, step=1, value=0, key="n2_mw")
                checks = {
                    "Grupos independientes": True,
                    "Normalidad": False,
                }
                if n1 >= 5 and n2 >= 5:
                    checks["n >= 5 por grupo"] = True
                else:
                    checks["n >= 5 por grupo"] = (f"{n1} y {n2}", False) if (n1>0 or n2>0) else ("Tamaño no especificado", False)
                show_prueba_result("mann_whitney", checks)
            else:
                st.info("Si no estás seguro sobre normalidad, puedes calcular pruebas de normalidad (Shapiro-Wilk) o inspeccionar gráficos. Responde en base al resultado.")
        else:
            # Paired samples
            st.markdown("**Comparación pareada / muestras relacionadas**")
            normal_diffs = st.radio("4) ¿Las diferencias entre pares siguen una distribución aproximadamente normal?", ["Sí", "No", "No sé / No lo sé"])
            n_pairs = st.number_input("Número de pares (n pares) — opcional", min_value=0, step=1, value=0)
            if normal_diffs == "Sí":
                checks = {
                    "Muestras pareadas": True,
                    "Normalidad de diferencias": True,
                    "n pares >= 30 (recomendado)": n_pairs >= 30 if n_pairs>0 else ("Tamaño no especificado", False)
                }
                show_prueba_result("t_pareado", checks)
            elif normal_diffs == "No":
                checks = {
                    "Muestras pareadas": True,
                    "Normalidad de diferencias": False,
                    "n pares >= 10 (recomendado)": n_pairs >= 10 if n_pairs>0 else ("Tamaño no especificado", False)
                }
                show_prueba_result("wilcoxon", checks)
            else:
                st.info("Si no sabes la normalidad de las diferencias, calcula o inspecciona gráficos. Responde según el resultado.")
    else:
        # More than 2 groups
        st.markdown("**Comparación entre más de 2 grupos**")
        normal = st.radio("3) ¿Los datos son aproximadamente normales en cada grupo?", ["Sí", "No", "No sé / No lo sé"])
        hom = None
        if normal == "Sí":
            hom = st.radio("4) ¿Las varianzas son aproximadamente homogéneas (Levene)?", ["Sí", "No", "No sé / No lo sé"])
        # Ask for number of groups and sample sizes per group optionally
        k = st.number_input("Número de grupos (k)", min_value=3, step=1, value=3)
        sample_sizes = []
        cols = st.columns(min(k, 6))
        # allow up to 6 inputs inline; if more, will be stacked
        for i in range(k):
            key = f"gsize_{i}"
            if i < 6:
                sample_sizes.append(cols[i % len(cols)].number_input(f"n grupo {i+1}", min_value=0, step=1, value=0, key=key))
            else:
                sample_sizes.append(st.number_input(f"n grupo {i+1}", min_value=0, step=1, value=0, key=key))
        min_n = min(sample_sizes) if sample_sizes else 0

        if normal == "Sí" and hom == "Sí":
            # ANOVA
            checks = {
                "Normalidad en grupos": True,
                "Homogeneidad de varianzas": True,
                "Grupos independientes": True,
                "k (>=3) registrado": k >= 3
            }
            if min_n >= 30:
                checks["n >= 30 por grupo"] = True
            else:
                checks["n >= 30 por grupo"] = (f"mín {min_n}", False) if min_n>0 else ("Tamaño no especificado", False)
            show_prueba_result("anova", checks)
        else:
            # Kruskal
            checks = {
                "Normalidad en grupos": False if normal == "No" else ("No seguro", False),
                "Grupos independientes": True,
                "Datos al menos ordinales": True,
                "k (>=3) registrado": k >= 3
            }
            if min_n >= 5:
                checks["n >= 5 por grupo"] = True
            else:
                checks["n >= 5 por grupo"] = (f"mín {min_n}", False) if min_n>0 else ("Tamaño no especificado", False)
            show_prueba_result("kruskal", checks)

# ---------- Asociar variables ----------
elif choice == "Asociar variables":
    st.markdown("**Asociar variables**")
    tipo = st.radio("2) ¿Qué tipo de variables vas a analizar?", ["Dos variables numéricas", "Dos variables categóricas", "Numerica dependiente y numerica independiente (predicción simple)"])
    if tipo == "Dos variables numéricas":
        normal = st.radio("3) ¿Ambas variables siguen una distribución aproximadamente normal?", ["Sí", "No", "No sé / No lo sé"])
        n_obs = st.number_input("Número total de observaciones (n) — opcional", min_value=0, step=1, value=0)
        if normal == "Sí":
            checks = {
                "Ambas variables numéricas": True,
                "Normalidad en ambas": True,
                "Relación lineal (verificar con scatter)": True
            }
            if n_obs >= 30:
                checks["n >= 30 (recomendado)"] = True
            else:
                checks["n >= 30 (recomendado)"] = (f"n={n_obs}", False) if n_obs>0 else ("n no especificado", False)
            show_prueba_result("pearson", checks)
        else:
            checks = {
                "Ambas variables numéricas u ordinales": True,
                "Normalidad no cumplida": True,
            }
            show_prueba_result("spearman", checks)
    elif tipo == "Dos variables categóricas":
        st.markdown("**Chi-cuadrada de independencia**")
        # Let the user optionally input contingency table sizes or expected counts
        n_total = st.number_input("Tamaño de la muestra total (n) — opcional", min_value=0, step=1, value=0)
        pct_cells_ok = st.slider("¿Qué % aproximado de celdas tienen frecuencia esperada >=5? (si no sabes, deja en 0)", 0, 100, 80)
        checks = {
            "Variables categóricas": True,
            "Muestra suficientemente grande (>=20 sugerido)": n_total >= 20 if n_total>0 else ("n no especificado", False),
            ">=80% celdas con esperada >=5": pct_cells_ok >= 80
        }
        show_prueba_result("chi2", checks)
    else:
        # Prediction with single predictor
        st.markdown("**Regresión lineal simple**")
        n_obs = st.number_input("Número de observaciones (n) — opcional", min_value=0, step=1, value=0)
        st.write("Responde las siguientes preguntas sobre supuestos (puedes revisar residuos gráficamente si tienes los datos).")
        linear = st.radio("Relación aproximadamente lineal (scatter)?", ["Sí", "No", "No sé"])
        indep_resid = st.radio("¿Los residuos son independientes (no hay autocorrelación)?", ["Sí", "No", "No sé"])
        homos = st.radio("¿Los residuos muestran varianza constante (homocedasticidad)?", ["Sí", "No", "No sé"])
        normal_res = st.radio("¿Los residuos son aproximadamente normales?", ["Sí", "No", "No sé"])
        checks = {
            "Relación lineal": linear == "Sí",
            "Independencia de residuos": indep_resid == "Sí",
            "Homocedasticidad": homos == "Sí",
            "Normalidad de residuos": normal_res == "Sí",
            "n especificado (recomendado mayor que ~30)": n_obs >= 30 if n_obs>0 else ("n no especificado", False)
        }
        show_prueba_result("regresion", checks)

# ---------- Predicción (directo a regresión) ----------
else:
    st.markdown("**Predicción (Regresión lineal simple)**")
    n_obs = st.number_input("Número de observaciones (n) — opcional", min_value=0, step=1, value=0)
    linear = st.radio("Relación aproximadamente lineal (scatter)?", ["Sí", "No", "No sé"])
    indep_resid = st.radio("¿Los residuos son independientes (no hay autocorrelación)?", ["Sí", "No", "No sé"], key="indep2")
    homos = st.radio("¿Los residuos muestran varianza constante (homocedasticidad)?", ["Sí", "No", "No sé"], key="homos2")
    normal_res = st.radio("¿Los residuos son aproximadamente normales?", ["Sí", "No", "No sé"], key="normres2")
    checks = {
        "Relación lineal": linear == "Sí",
        "Independencia de residuos": indep_resid == "Sí",
        "Homocedasticidad": homos == "Sí",
        "Normalidad de residuos": normal_res == "Sí",
        "n especificado (recomendado mayor que ~30)": n_obs >= 30 if n_obs>0 else ("n no especificado", False)
    }
    show_prueba_result("regresion", checks)

# ---------- Footer: ayuda y referencias ----------
st.write("---")
st.subheader("Cómo interpretar esto")
st.write(dedent("""
- La herramienta **recomienda** la prueba más adecuada según tus respuestas y muestra los supuestos y criterios.
- Las comprobaciones que realiza aquí son **simples** (basadas en respuestas del usuario y tamaños mínimos). Para mayor rigor, se recomienda:
  - Calcular pruebas de normalidad (Shapiro-Wilk) o inspeccionar gráficos Q-Q y histogramas.
  - Verificar homogeneidad de varianzas con la prueba de Levene.
  - En tablas de contingencia, revisar frecuencias esperadas y, si impera, agrupar categorías o usar Fisher.
- Si tienes los datos crudos y quieres, puedo:
  - Generar el código que ejecute las pruebas automáticas (Shapiro, Levene, t, Mann-Whitney, ANOVA, Kruskal, chi2, Pearson/Spearman, regresión) y muestre resultados.
"""))

st.caption("Basado en la tabla de pruebas que proporcionaste (completada y estandarizada para coherencia).")

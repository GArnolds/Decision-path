# streamlit_app.py
import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats

st.set_page_config(page_title="Árbol de decisión estadístico (interactivo)", layout="wide")

st.title("🧠 Árbol interactivo: ¿Qué prueba estadística debo usar?")
st.write("Responde las preguntas paso a paso. Opcionalmente puedes subir un CSV para que la app compruebe supuestos automáticamente.")

st.sidebar.header("Carga de datos (opcional)")
uploaded = st.sidebar.file_uploader("Sube un CSV con tus datos (columnas nombradas)", type=["csv"])

# Utilidades para comprobaciones automáticas
def safe_shapiro(arr):
    """Devuelve (ok_bool, pvalue, msg). ok_bool=True si p>0.05 (normal)."""
    arr = np.array(arr.dropna())
    if arr.size < 3:
        return (False, None, "Muestra menor a 3 → no se puede comprobar Shapiro")
    try:
        stat, p = stats.shapiro(arr)
        return (p > 0.05, p, f"Shapiro p={p:.4f}")
    except Exception as e:
        return (False, None, f"Shapiro error: {e}")

def safe_levene(*groups):
    """Devuelve (ok_bool, pvalue, msg). ok_bool=True si p>0.05 (varianzas homogéneas)."""
    clean_groups = [np.array(g.dropna()) for g in groups]
    try:
        stat, p = stats.levene(*clean_groups)
        return (p > 0.05, p, f"Levene p={p:.4f}")
    except Exception as e:
        return (False, None, f"Levene error: {e}")

def sample_size_ok(n, threshold):
    return (n >= threshold, n)

# Si se subió CSV, lo cargamos y mostramos columnas
df = None
if uploaded:
    try:
        df = pd.read_csv(uploaded)
        st.sidebar.success("CSV cargado correctamente.")
        st.sidebar.write("Columnas detectadas:")
        st.sidebar.dataframe(pd.DataFrame({"columnas": df.columns}))
    except Exception as e:
        st.sidebar.error(f"No se pudo leer CSV: {e}")

st.markdown("---")

# ---------- Flujo interactivo ----------
st.header("1) ¿Qué quieres analizar?")
choice = st.radio("", ["Comparar grupos", "Asociar variables", "Predicción (regresión)"])

# ---------- COMPARE GROUPS ----------
if choice == "Comparar grupos":
    st.subheader("Comparar grupos")
    # opcion para usar columnas del df
    use_csv = st.checkbox("Usar columnas del CSV (si cargaste uno)", value=False) if df is not None else False

    if use_csv and df is not None:
        st.info("Selecciona la columna que indica el grupo (categórica) y la columna numérica (dependiente).")
        group_col = st.selectbox("Columna de grupo (categoría)", df.columns)
        value_col = st.selectbox("Columna de valores (numérica)", df.columns)
        # Preparamos grupos
        groups = []
        group_names = df[group_col].dropna().unique().tolist()
        for g in group_names:
            groups.append(df.loc[df[group_col] == g, value_col])
        st.write(f"Grupos detectados ({len(group_names)}): {group_names}")
        # número de grupos
        k = len(group_names)
        st.write(f"Tamaño por grupo (primeros 10):")
        st.write({g: int((df.loc[df[group_col] == g, value_col].dropna().shape[0])) for g in group_names})
    else:
        k = st.radio("¿Cuántos grupos comparas?", ["2 grupos", "Más de 2 grupos"])
        if k == "2 grupos":
            # pedir info de tamaños (opcionales)
            n1 = st.number_input("Tamaño grupo 1 (opcional)", min_value=0, step=1, value=0)
            n2 = st.number_input("Tamaño grupo 2 (opcional)", min_value=0, step=1, value=0)
            groups = None
            group_names = None
        else:
            # más de 2 grupos: preguntar k
            k_num = st.number_input("Número de grupos (k)", min_value=3, step=1, value=3)
            st.write("Para comprobaciones automáticas sube CSV con columnas, o introduce tamaños manuales si lo deseas.")
            groups = None
            group_names = None

    # Pregunta normalidad (si no se puede calcular con CSV, preguntar al usuario)
    if df is not None and use_csv:
        # si k==2 o k>2, podemos ejecutar Shapiro por grupo
        normal_per_group = {}
        pvals_shapiro = {}
        for i, g in enumerate(group_names):
            ok, p, msg = safe_shapiro(df.loc[df[group_col] == g, value_col])
            normal_per_group[g] = ok
            pvals_shapiro[g] = (p, msg)
        st.write("Comprobación automática de normalidad (Shapiro) por grupo:")
        for g in group_names:
            p, msg = pvals_shapiro[g]
            if p is None:
                st.write(f"- {g}: {msg}")
            else:
                st.write(f"- {g}: p={p:.4f} → {'normal' if normal_per_group[g] else 'no normal'}")
        # Levene para homogeneidad si hay al menos 2 grupos
        if len(group_names) >= 2:
            lev_ok, lev_p, lev_msg = safe_levene(*[df.loc[df[group_col] == g, value_col] for g in group_names])
            st.write(f"Prueba de Levene (homogeneidad de varianzas): {lev_msg} → {'homogéneas' if lev_ok else 'no homogéneas'}")
    else:
        st.write("Si no subes datos, responde las siguientes preguntas según tu conocimiento:")
        normal = st.radio("¿Los datos en los grupos siguen una distribución aproximadamente normal?", ["Sí", "No", "No sé"])
        if k == "2 grupos" or (isinstance(k, str) and k == "2 grupos"):
            indep = st.radio("¿Las muestras son independientes o pareadas?", ["Independientes", "Pareadas / relacionadas"])
        else:
            indep = st.radio("¿Los grupos son independientes (asumo sí)?", ["Sí", "No"])

    # Decisión final (automática si df dadas, o a partir de respuestas)
    st.markdown("**Resultado recomendado:**")
    # Si tenemos df y group_names
    if df is not None and use_csv:
        if len(group_names) == 2:
            # check normality both
            normals = [normal_per_group[g] for g in group_names]
            if all(normals):
                if lev_ok:
                    st.success("t de Student (muestras independientes o pareadas según el diseño).")
                    st.write("- Nota: verifica si son independientes o pareados según tu diseño.")
                else:
                    st.success("t de Student (siempre que diseño y supuestos permitan), pero Levene sugiere no homogeneidad → considerar Welch t o Mann–Whitney.")
            else:
                st.success("U de Mann–Whitney (no paramétrica), ya que al menos un grupo no es normal.")
        elif len(group_names) > 2:
            # check if any normal false
            if all(normal_per_group[g] for g in group_names) and lev_ok:
                st.success("ANOVA de un factor (paramétrica).")
            else:
                st.success("Kruskal–Wallis (no paramétrica).")
        else:
            st.warning("No se pudieron detectar correctamente los grupos. Revisa el CSV.")
    else:
        # sin CSV: basarse en respuestas
        try:
            if k == "2 grupos":
                if normal == "Sí":
                    if indep == "Independientes":
                        st.success("t de Student (muestras independientes)")
                    else:
                        st.success("t de Student (muestras pareadas)")
                elif normal == "No":
                    if indep == "Independientes":
                        st.success("U de Mann–Whitney")
                    else:
                        st.success("Wilcoxon (pareada)")
                else:
                    st.info("Si no estás seguro, considera comprobar normalidad con Shapiro o ver histogramas.")
            else:
                # más de 2 grupos
                if normal == "Sí" and indep == "Sí":
                    st.success("ANOVA de un factor")
                else:
                    st.success("Kruskal–Wallis")
        except Exception:
            st.error("No fue posible tomar una decisión automática con los inputs actuales.")

    st.markdown("---")
    st.info("Si quieres que la app ejecute la prueba y muestre p-value, sube tu CSV con las columnas de grupo y valores, o dime y te agrego la ejecución automática de la prueba.")

# ---------- ASOCIAR VARIABLES ----------
elif choice == "Asociar variables":
    st.subheader("Asociar variables (correlación / asociación)")
    if df is not None:
        st.info("Si cargaste CSV, selecciona las columnas para el análisis.")
        col1 = st.selectbox("Variable 1 (columna)", df.columns)
        col2 = st.selectbox("Variable 2 (columna)", df.columns, index=1 if len(df.columns) > 1 else 0)
        v1 = df[col1].dropna()
        v2 = df[col2].dropna()
        st.write(f"N registros (sin NA): {min(len(v1), len(v2))}")
        # decidir tipo: numéricas o categóricas según dtype / nunique
        is_num1 = pd.api.types.is_numeric_dtype(v1)
        is_num2 = pd.api.types.is_numeric_dtype(v2)

        if is_num1 and is_num2:
            # test de normalidad en ambas
            ok1, p1, m1 = safe_shapiro(v1)
            ok2, p2, m2 = safe_shapiro(v2)
            st.write(f"Shapiro V1: {m1} — {'normal' if ok1 else 'no normal'}")
            st.write(f"Shapiro V2: {m2} — {'normal' if ok2 else 'no normal'}")
            if ok1 and ok2:
                r, p = stats.pearsonr(v1, v2)
                st.success(f"Correlación de Pearson: r={r:.3f}, p={p:.4f}")
            else:
                r, p = stats.spearmanr(v1, v2)
                st.success(f"Correlación de Spearman: rho={r:.3f}, p={p:.4f}")
        elif (not is_num1 and not is_num2) or (pd.api.types.is_categorical_dtype(v1) or pd.api.types.is_categorical_dtype(v2)):
            st.success("Chi-cuadrada de independencia (si ambas son categóricas). Construye tabla de contingencia.")
            ct = pd.crosstab(df[col1], df[col2])
            st.write("Tabla de contingencia:")
            st.dataframe(ct)
            try:
                chi2, p, dof, expected = stats.chi2_contingency(ct)
                st.write(f"Chi2={chi2:.3f}, p={p:.4f}, dof={dof}")
            except Exception as e:
                st.error(f"No se pudo calcular chi-cuadrada: {e}")
        else:
            st.info("Si una variable es numérica y otra categórica, considera comparar medias (t/ANOVA) o resumir por grupos.")
    else:
        st.write("Sin datos, responde estas preguntas:")
        tipo = st.radio("Tipo de variables", ["Dos numéricas", "Dos categóricas", "Numérica y categórica"])
        if tipo == "Dos numéricas":
            corr_normal = st.radio("¿Ambas normales?", ["Sí", "No"])
            if corr_normal == "Sí":
                st.success("Correlación de Pearson (si relación lineal).")
            else:
                st.success("Correlación de Spearman (monótona / ordinal).")
        elif tipo == "Dos categóricas":
            st.success("Chi-cuadrada de independencia")
        else:
            st.info("Numérica + categórica → comparación de medias (t/ANOVA) o pruebas no paramétricas según supuestos.")

# ---------- REGRESIÓN ----------
elif choice == "Predicción (regresión)":
    st.subheader("Regresión lineal simple")
    st.write("Puedes subir CSV con la variable dependiente (y) y la independiente (x) para que la app ajuste un modelo simple.")
    if df is not None:
        y_col = st.selectbox("Variable dependiente (y)", df.columns)
        x_col = st.selectbox("Variable independiente (x)", df.columns, index=1 if len(df.columns) > 1 else 0)
        y = df[y_col].dropna()
        x = df[x_col].dropna()
        if len(x) < 3 or len(y) < 3:
            st.warning("Pocos datos para ajustar un modelo (recomendado n >= 30).")
        else:
            try:
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                st.success(f"Regresión lineal simple: y = {intercept:.3f} + {slope:.3f} x")
                st.write(f"R² = {r_value**2:.3f}, p (pendiente) = {p_value:.4f}")
            except Exception as e:
                st.error(f"No se pudo ajustar regresión: {e}")
    else:
        st.info("Sin CSV, la recomendación general es: comprobar linealidad, homocedasticidad e independencia de residuos. Si todo ok → regresión lineal simple.")

st.markdown("---")
st.caption("App creada para guiar la selección de pruebas. Puedo adaptar umbrales, mensajes y añadir ejecución automática de pruebas si lo deseas.")

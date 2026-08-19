import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime

# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="ANDINA CRM · RFM",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# ESTILOS
# ============================================================

st.markdown("""
<style>

.main {
    background-color: #f7f8fa;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    font-weight: 700;
}

.metric-card {
    background: white;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #e8e8e8;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.segment-card {
    background: white;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #e8e8e8;
    margin-bottom: 10px;
}

.small-text {
    color: #6b7280;
    font-size: 0.85rem;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# VARIABLES
# ============================================================

REQUIRED_COLUMNS = [
    "ClienteID",
    "Nombre",
    "Tipo",
    "Ciudad",
    "UltimaCompra",
    "Compras",
    "ValorTotal",
    "Categoria",
    "Canal"
]


# ============================================================
# FUNCIONES
# ============================================================

def validate_columns(df):

    missing = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    return missing


def calculate_rfm(df):

    data = df.copy()

    # Fecha
    data["UltimaCompra"] = pd.to_datetime(
        data["UltimaCompra"],
        errors="coerce"
    )

    # Numéricos
    data["Compras"] = pd.to_numeric(
        data["Compras"],
        errors="coerce"
    ).fillna(0)

    data["ValorTotal"] = pd.to_numeric(
        data["ValorTotal"],
        errors="coerce"
    ).fillna(0)

    # Fecha de referencia
    fecha_referencia = data["UltimaCompra"].max()

    # Recency
    data["Recency"] = (
        fecha_referencia - data["UltimaCompra"]
    ).dt.days

    data["Recency"] = data["Recency"].fillna(
        data["Recency"].max()
    )

    # Frequency
    data["Frequency"] = data["Compras"]

    # Monetary
    data["Monetary"] = data["ValorTotal"]

    # ========================================================
    # SCORING
    # ========================================================

    # Recency:
    # menor cantidad de días = mejor score
    data["R_Score"] = pd.qcut(
        data["Recency"].rank(method="first"),
        5,
        labels=[5, 4, 3, 2, 1]
    ).astype(int)

    # Frequency
    data["F_Score"] = pd.qcut(
        data["Frequency"].rank(method="first"),
        5,
        labels=[1, 2, 3, 4, 5]
    ).astype(int)

    # Monetary
    data["M_Score"] = pd.qcut(
        data["Monetary"].rank(method="first"),
        5,
        labels=[1, 2, 3, 4, 5]
    ).astype(int)

    # Código RFM
    data["RFM_Score"] = (
        data["R_Score"].astype(str)
        + data["F_Score"].astype(str)
        + data["M_Score"].astype(str)
    )

    # Score promedio
    data["RFM_Total"] = (
        data["R_Score"]
        + data["F_Score"]
        + data["M_Score"]
    )

    # Segmentación
    data["Segmento"] = data.apply(
        classify_segment,
        axis=1
    )

    return data, fecha_referencia


def classify_segment(row):

    r = row["R_Score"]
    f = row["F_Score"]
    m = row["M_Score"]

    # Campeones
    if r >= 4 and f >= 4 and m >= 4:
        return "Campeones"

    # Clientes leales
    if r >= 4 and f >= 4:
        return "Clientes Leales"

    # Alto valor / riesgo
    if r <= 2 and f >= 4 and m >= 4:
        return "No Podemos Perderlos"

    # En riesgo
    if r <= 2 and f >= 3:
        return "En Riesgo"

    # Potenciales
    if r >= 4 and f <= 3 and m >= 3:
        return "Potenciales"

    # Nuevos
    if r >= 4 and f <= 2:
        return "Nuevos Clientes"

    # Hibernando
    if r <= 2 and f <= 2 and m >= 3:
        return "Hibernando"

    # Perdidos
    if r <= 2 and f <= 2:
        return "Perdidos"

    return "Necesitan Atención"


def export_excel(df):

    output = io.BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="Clientes"
        )

    return output.getvalue()


def export_all_segments(df):

    output = io.BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        for segmento in sorted(
            df["Segmento"].unique()
        ):

            segment_df = df[
                df["Segmento"] == segmento
            ]

            sheet_name = segmento[:31]

            segment_df.to_excel(
                writer,
                index=False,
                sheet_name=sheet_name
            )

    return output.getvalue()


# ============================================================
# HEADER
# ============================================================

st.title("ANDINA CRM · Segmentación RFM")

st.markdown(
    "Clasificación inteligente de clientes para marketing y CRM."
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("📁 Cargar clientes")

    uploaded_file = st.file_uploader(
        "Sube tu archivo CSV",
        type=["csv"]
    )

    st.caption(
        "Columnas requeridas: ClienteID, Nombre, Tipo, "
        "Ciudad, UltimaCompra, Compras, ValorTotal, "
        "Categoria y Canal."
    )


# ============================================================
# CARGA DE DATOS
# ============================================================

if uploaded_file is None:

    st.info(
        "👆 Sube un CSV para comenzar el análisis RFM."
    )

    st.markdown("""
    ### ¿Qué analiza este CRM?

    **R — Recency**  
    ¿Hace cuánto compró?

    **F — Frequency**  
    ¿Cuántas veces compra?

    **M — Monetary**  
    ¿Cuánto dinero representa?

    El sistema convierte estas variables en una
    segmentación accionable para marketing.
    """)

    st.stop()


# ============================================================
# LECTURA
# ============================================================

try:

    df = pd.read_csv(uploaded_file)

except Exception:

    st.error(
        "No fue posible leer el CSV. "
        "Verifica que el archivo tenga formato CSV válido."
    )

    st.stop()


# ============================================================
# VALIDACIÓN
# ============================================================

missing_columns = validate_columns(df)

if missing_columns:

    st.error(
        "El archivo no contiene todas las columnas requeridas."
    )

    st.write(
        "Columnas faltantes:",
        missing_columns
    )

    st.stop()


# ============================================================
# RFM
# ============================================================

rfm, reference_date = calculate_rfm(df)


# ============================================================
# FILTROS
# ============================================================

st.sidebar.divider()

st.sidebar.header("🎯 Filtros")

selected_city = st.sidebar.multiselect(
    "Ciudad",
    sorted(rfm["Ciudad"].dropna().unique())
)

selected_type = st.sidebar.multiselect(
    "Tipo de cliente",
    sorted(rfm["Tipo"].dropna().unique())
)

selected_category = st.sidebar.multiselect(
    "Categoría",
    sorted(rfm["Categoria"].dropna().unique())
)

selected_channel = st.sidebar.multiselect(
    "Canal",
    sorted(rfm["Canal"].dropna().unique())
)

selected_segment = st.sidebar.multiselect(
    "Segmento RFM",
    sorted(rfm["Segmento"].unique())
)


filtered = rfm.copy()

if selected_city:
    filtered = filtered[
        filtered["Ciudad"].isin(selected_city)
    ]

if selected_type:
    filtered = filtered[
        filtered["Tipo"].isin(selected_type)
    ]

if selected_category:
    filtered = filtered[
        filtered["Categoria"].isin(selected_category)
    ]

if selected_channel:
    filtered = filtered[
        filtered["Canal"].isin(selected_channel)
    ]

if selected_segment:
    filtered = filtered[
        filtered["Segmento"].isin(selected_segment)
    ]


# ============================================================
# KPIs
# ============================================================

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Clientes",
        f"{len(filtered):,}"
    )

with col2:
    st.metric(
        "Valor total",
        f"${filtered['Monetary'].sum():,.0f}"
    )

with col3:
    st.metric(
        "Compras",
        f"{filtered['Frequency'].sum():,.0f}"
    )

with col4:

    avg_ticket = (
        filtered["Monetary"].sum()
        / filtered["Frequency"].sum()
        if filtered["Frequency"].sum() > 0
        else 0
    )

    st.metric(
        "Ticket promedio",
        f"${avg_ticket:,.0f}"
    )

with col5:

    avg_recency = (
        filtered["Recency"].mean()
        if len(filtered) > 0
        else 0
    )

    st.metric(
        "Recencia promedio",
        f"{avg_recency:.0f} días"
    )


st.divider()


# ============================================================
# DASHBOARD
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Dashboard",
    "👥 Segmentación",
    "🔎 Clientes",
    "📥 Exportar"
])


# ============================================================
# TAB 1
# ============================================================

with tab1:

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Clientes por segmento")

        segment_counts = (
            filtered["Segmento"]
            .value_counts()
        )

        st.bar_chart(
            segment_counts
        )

    with col2:

        st.subheader("Valor por segmento")

        segment_value = (
            filtered
            .groupby("Segmento")["Monetary"]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(
            segment_value
        )


    st.subheader("Distribución por ciudad")

    city_data = (
        filtered
        .groupby("Ciudad")
        .agg(
            Clientes=("ClienteID", "count"),
            Valor=("Monetary", "sum")
        )
        .sort_values(
            "Valor",
            ascending=False
        )
    )

    st.dataframe(
        city_data,
        use_container_width=True
    )


# ============================================================
# TAB 2
# ============================================================

with tab2:

    st.subheader("Segmentación RFM")

    segment_summary = (
        filtered
        .groupby("Segmento")
        .agg(
            Clientes=("ClienteID", "count"),
            ValorTotal=("Monetary", "sum"),
            Compras=("Frequency", "sum"),
            RecenciaPromedio=("Recency", "mean")
        )
        .sort_values(
            "ValorTotal",
            ascending=False
        )
    )

    segment_summary[
        "Participación"
    ] = (
        segment_summary["Clientes"]
        / len(filtered)
        * 100
    )

    st.dataframe(
        segment_summary.style.format({
            "ValorTotal": "${:,.0f}",
            "Compras": "{:,.0f}",
            "RecenciaPromedio": "{:.0f}",
            "Participación": "{:.1f}%"
        }),
        use_container_width=True
    )


# ============================================================
# TAB 3
# ============================================================

with tab3:

    st.subheader("Explorador de clientes")

    columns_to_show = [
        "ClienteID",
        "Nombre",
        "Tipo",
        "Ciudad",
        "UltimaCompra",
        "Compras",
        "ValorTotal",
        "Categoria",
        "Canal",
        "Recency",
        "Frequency",
        "Monetary",
        "R_Score",
        "F_Score",
        "M_Score",
        "RFM_Score",
        "Segmento"
    ]

    st.dataframe(
        filtered[columns_to_show],
        use_container_width=True,
        height=600
    )


# ============================================================
# TAB 4
# ============================================================

with tab4:

    st.subheader("Descargar segmentos")

    st.markdown(
        "Selecciona un segmento para descargar "
        "su base comercial."
    )

    available_segments = sorted(
        filtered["Segmento"].unique()
    )

    selected_download_segment = st.selectbox(
        "Segmento",
        available_segments
    )

    segment_download = filtered[
        filtered["Segmento"]
        == selected_download_segment
    ]

    excel_segment = export_excel(
        segment_download
    )

    st.download_button(
        label=f"⬇️ Descargar {selected_download_segment}",
        data=excel_segment,
        file_name=(
            f"ANDINA_{selected_download_segment}.xlsx"
        ),
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )

    st.divider()

    st.subheader("Descargar todos los segmentos")

    excel_all = export_all_segments(
        filtered
    )

    st.download_button(
        label="⬇️ Descargar todos los segmentos",
        data=excel_all,
        file_name="ANDINA_RFM_SEGMENTOS.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    f"ANDINA CRM · Modelo RFM · Fecha de referencia: "
    f"{reference_date.strftime('%Y-%m-%d')}"
)

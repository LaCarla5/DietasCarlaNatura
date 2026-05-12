import streamlit as st
import pandas as pd
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import datetime
import plotly.express as px

# --- 1. CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="Dietas Carla Natura",
                   layout="wide", page_icon="🥗")

# Inicialización de seguridad para evitar KeyError y errores de descarga
if "df_final" not in st.session_state:
    st.session_state["df_final"] = None
if "pdf_bytes" not in st.session_state:
    st.session_state["pdf_bytes"] = None
if "acumulado" not in st.session_state:
    st.session_state["acumulado"] = None

st.markdown("""
<style>
    /* Botones generales */
    .stButton>button { 
        background-color: #264d21; 
        color: white; 
        border-radius: 10px; 
    }
    
    /* Títulos */
    h1, h2, h3 { color: #264d21; }

    /* CAMBIO DE COLOR EN SELECTS (MULTISELECT TAGS) */
    span[data-baseweb="tag"] {
        background-color: #264d21 !important;
        color: white !important;
    }
    
    /* Icono X de los tags */
    span[data-baseweb="tag"] svg {
        fill: white !important;
    }

    /* Borde del selector al hacer clic */
    div[data-baseweb="select"] {
        border-color: #264d21 !important;
    }
    
    /* Color de las métricas (Peso/Meta) */
    [data-testid="stMetricValue"] {
        color: #264d21 !important;
    }
    
    /* Estilo para la tarjeta de la métrica */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #264d21; /* Tu verde */
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }

    /* Forzar color verde en el valor y la etiqueta */
    [data-testid="stMetricLabel"] p {
        color: #264d21 !important;
        font-weight: bold !important;
    }

    [data-testid="stMetricValue"] {
        color: #264d21 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. FUNCIONES DE CARGA Y PDF ---
SHEET_ID = "14hOSakCs0yfF7WFB1nQAW0b_LqRRHkIxLzHY1u1V9PA"
URL_ING = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"


@st.cache_data(ttl=60)
def cargar_datos(url):
    try:
        df = pd.read_csv(url)
        df.columns = [str(c).strip() for c in df.columns]
        return df.dropna(how='all')
    except:
        return pd.DataFrame()


def generar_pdf_unico(resumen_menu, df_compra):
    verde_r, verde_g, verde_b = 38, 77, 33

    # Orientación Landscape (Horizontal) para la tabla del menú
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)

    dias_totales = list(resumen_menu.keys())
    momentos_lista = ["Desayuno", "Almuerzo", "Comida", "Merienda", "Cena"]

    # --- PÁGINA 1: TABLA SEMANAL HORIZONTAL ---
    # controlar que casa semana cree otra hoja
    for i in range(0, len(dias_totales), 7):
        pdf.add_page()
        # Seleccionamos solo los 7 días de esta semana
        dias_semana = dias_totales[i : i + 7]
        
        pdf.set_font("helvetica", "B", 16)
        pdf.set_text_color(verde_r, verde_g, verde_b)
        pdf.cell(0, 10, f"CALENDARIO NUTRICIONAL - SEMANA {int(i/7) + 1}", 
                    new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        pdf.ln(5)

        # Ajustamos el ancho de las columnas según cuántos días queden (por si la última semana es más corta)
        ancho_momento = 30
        ancho_dia = (277 - ancho_momento) / len(dias_semana)

        # Cabecera de la tabla (VERDE)
        pdf.set_font("helvetica", "B", 10)
        pdf.set_fill_color(verde_r, verde_g, verde_b)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(ancho_momento, 10, "Momento", 1, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C', fill=True)
        
        for dia in dias_semana:
            # Usamos dia.split()[0] para que solo salga "Lunes", "Martes", etc.
            pdf.cell(ancho_dia, 10, dia.split()[0], 1, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C', fill=True)
        pdf.ln()

        # Filas de la tabla
        pdf.set_text_color(0, 0, 0)
        for m in momentos_lista:
            y_inicio = pdf.get_y()
            pdf.set_font("helvetica", "B", 9)
            pdf.set_fill_color(240, 240, 240) # Gris clarito para los momentos
            pdf.cell(ancho_momento, 25, m, 1, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C', fill=True)

            pdf.set_font("helvetica", "", 8)
            for dia in dias_semana:
                platos = resumen_menu[dia].get(m, [])
                txt_platos = "\n".join(platos).encode('latin-1', 'replace').decode('latin-1')
                
                x_act = pdf.get_x()
                # Dibujamos el rectángulo de la celda
                pdf.rect(x_act, y_inicio, ancho_dia, 25)
                # Multi_cell para que el texto se ajuste dentro
                pdf.multi_cell(ancho_dia, 5, txt_platos, align='C')
                # Volvemos a la posición X para la siguiente columna, manteniendo la Y de la fila
                pdf.set_xy(x_act + ancho_dia, y_inicio)
            
            # Al terminar la fila de platos, bajamos la Y para el siguiente momento
            pdf.set_y(y_inicio + 25)

    # --- PÁGINA 2: PLAN DETALLADO (Vertical) ---
    pdf.add_page(orientation='P')  # Cambiamos a Vertical
    pdf.set_font("helvetica", "B", 16)
    pdf.set_text_color(verde_r, verde_g, verde_b)
    pdf.cell(0, 10, "DESGLOSE POR DÍAS",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(5)

    for dia, momentos_dict in resumen_menu.items():
        pdf.set_font("helvetica", "B", 11)
        pdf.set_fill_color(38, 77, 33)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(190, 8, f"  {dia.upper()}", border=1,
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
        pdf.set_text_color(0, 0, 0)

        for m in momentos_lista:
            platos = momentos_dict.get(m, [])
            if platos:
                pdf.set_font("helvetica", "B", 9)
                pdf.cell(190, 6, f" {m}:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_font("helvetica", "", 10)
                pdf.multi_cell(190, 6, " + ".join(platos).encode('latin-1', 'replace').decode(
                    'latin-1'), border='B', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(3)

    # --- PÁGINA 3: LISTA DE LA COMPRA ---
    pdf.add_page(orientation='P')
    pdf.set_font("helvetica", "B", 16)
    
    # 1. Título de la hoja (Texto en Verde)
    pdf.set_text_color(verde_r, verde_g, verde_b)
    pdf.cell(0, 10, "LISTA DE LA COMPRA",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(5)

    # 2. Cabecera de la tabla (Fondo Verde, Texto Blanco)
    pdf.set_fill_color(verde_r, verde_g, verde_b)
    pdf.set_text_color(255, 255, 255) # <--- Texto Blanco para el fondo verde
    pdf.set_font("helvetica", "B", 10)
    
    pdf.cell(110, 10, " Producto", 1, new_x=XPos.RIGHT,
             new_y=YPos.TOP, fill=True)
    pdf.cell(40, 10, " Cantidad", 1, new_x=XPos.RIGHT,
             new_y=YPos.TOP, align='C', fill=True)
    pdf.cell(40, 10, " Kcal", 1, new_x=XPos.LMARGIN,
             new_y=YPos.NEXT, align='C', fill=True)

    # 3. Cuerpo de la tabla (Resetear a Texto Negro para que se vea en el blanco)
    pdf.set_text_color(0, 0, 0) # <--- VOLVEMOS AL NEGRO (o usa verde_r, g, b si prefieres)
    pdf.set_font("helvetica", "", 10)
    
    for _, fila in df_compra.iterrows():
        y_at = pdf.get_y()
        # Dibujamos la celda de ingrediente
        pdf.multi_cell(110, 10, f" {str(fila['Ingrediente'])[:45]}", border=1)
        
        # Reposicionamos para las columnas de cantidad y kcal
        pdf.set_xy(120, y_at)
        pdf.cell(40, 10, f"{fila['Cantidad']:.2f} {fila['Unidad']}",
                 1, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')
        pdf.cell(40, 10, f"{int(fila['Kcal_Totales'])}", 1,
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

    # Conversión de seguridad
    return bytes(pdf.output())


# --- 3. SIDEBAR Y VALIDACIÓN ---
with st.sidebar:
    st.header("👤 Perfil")
    f_ini = st.date_input("Inicio", datetime.date.today())
    f_fin = st.date_input("Fin", datetime.date.today() +
                          datetime.timedelta(days=6))
    st.divider()

    # Pesos inicializados en 0
    peso = st.number_input("Peso Actual (Kg)", min_value=0, value=0, step=1)
    peso_obj = st.number_input(
        "Peso Objetivo (Kg)", min_value=0, value=0, step=1)

    # Variable para controlar si el perfil está completo
    perfil_completo = peso > 0 and peso_obj > 0

    if perfil_completo:
        # Creamos dos columnas para mostrar los pesos actuales de forma limpia
        c1, c2 = st.columns(2)
        c1.metric("Peso Actual", f"{peso} Kg")
        c2.metric("Objetivo", f"{peso_obj} Kg")
        
        st.divider()
        
        # Cálculo de la diferencia
        diff = abs(peso - peso_obj)
        
        if peso > peso_obj:
            # Caso: Perder peso
            st.metric(
                label="Meta Final (A perder)", 
                value=f"{diff} Kg", 
                delta=f"- {diff} Kg", 
                delta_color="normal" # Streamlit lo pondrá rojo automáticamente, o puedes usar CSS para cambiarlo
            )
        elif peso < peso_obj:
            # Caso: Ganar peso (Músculo)
            st.metric(
                label="Meta Final (A ganar)", 
                value=f"{diff} Kg", 
                delta=f"+ {diff} Kg", 
                delta_color="normal" # Streamlit lo pondrá verde
            )
        else:
            st.success("¡Estás en tu peso ideal! Mantenimiento activo. 🌿")
    else:
        st.warning("⚠️ Introduce pesos mayores a 0 para calcular tu meta.")

# --- BLOQUEO DE CONTENIDO ---
if not perfil_completo:
    st.title("🥗 Bienvenido a Carla Natura")
    st.info("Para activar el gestor de comidas, por favor completa tu **Peso Actual** y **Peso Objetivo** en el menú de la izquierda.")
    st.stop()

# --- 5. CUERPO DE LA APP ---
st.title("🌿 Gestión de Dietas")
df_recetas = cargar_datos(URL_ING)

if not df_recetas.empty:
    DIAS = ["Lunes", "Martes", "Miércoles",
            "Jueves", "Viernes", "Sábado", "Domingo"]
    MOMENTOS = ["Desayuno", "Almuerzo", "Comida", "Merienda", "Cena"]
    c_plat = df_recetas.columns[0]

    num_dias = (f_fin - f_ini).days + 1
    # Lista de llaves para verificar si se ha seleccionado alguna comida
    todas_las_keys = []

    for i in range(num_dias):
        fecha = f_ini + datetime.timedelta(days=i)
        st.subheader(f"📅 {DIAS[fecha.weekday()]} {fecha.strftime('%d/%m')}")
        cols = st.columns(5)
        for j, m in enumerate(MOMENTOS):
            key = f"sel_{fecha}_{m}"
            todas_las_keys.append(key)
            st.multiselect(m, sorted(df_recetas[c_plat].unique()), key=key)

    st.divider()

    # VALIDACIÓN: ¿Hay al menos una comida seleccionada?
    hay_comidas = any(len(st.session_state.get(k, []))
                      > 0 for k in todas_las_keys)

    # El botón se deshabilita si no hay comidas seleccionadas
    if st.button("📊 GENERAR INFORME NUTRICIONAL", disabled=not hay_comidas):
        # Lógica de generación (se mantiene igual que antes)
        acumulado = []
        resumen_kcal = {}
        for i in range(num_dias):
            fecha_l = f_ini + datetime.timedelta(days=i)
            tag = f"{DIAS[fecha_l.weekday()]} {fecha_l.strftime('%d/%m')}"
            resumen_kcal[tag] = {}
            for m in MOMENTOS:
                sel = st.session_state.get(f"sel_{fecha_l}_{m}", [])
                resumen_kcal[tag][m] = sel
                for p in sel:
                    ingreds = df_recetas[df_recetas[c_plat] == p]
                    for _, row in ingreds.iterrows():
                        try:
                            g = float(
                                str(row[df_recetas.columns[2]]).replace(',', '.'))
                            kc100 = float(
                                str(row[df_recetas.columns[5]]).replace(',', '.'))
                            kc_item = (
                                g * kc100 / 100) if str(row[df_recetas.columns[3]]).lower() in ['g', 'ml'] else (g * kc100)
                            acumulado.append(
                                {"Plato": p, "Ingrediente": row[df_recetas.columns[1]], "Cantidad": g, "Unidad": row[df_recetas.columns[3]], "Kcal_Totales": kc_item})
                        except:
                            continue

        if acumulado:
            df_final = pd.DataFrame(acumulado).groupby(['Ingrediente', 'Unidad']).agg(
                {'Cantidad': 'sum', 'Kcal_Totales': 'sum'}).reset_index()
            st.session_state["df_final"] = df_final
            st.session_state["acumulado"] = acumulado
            st.session_state["pdf_bytes"] = generar_pdf_unico(
                resumen_kcal, df_final)
            st.rerun()

# --- 6. RESULTADOS ---
res_df = st.session_state.get("df_final")
res_pdf = st.session_state.get("pdf_bytes")

if res_df is not None:
    st.header("📊 Resumen")
    st.plotly_chart(px.bar(pd.DataFrame(
        st.session_state["acumulado"]), x='Kcal_Totales', y='Plato', color='Ingrediente', orientation='h'))

    if res_pdf:
        st.download_button(
            label="📥 Descargar Plan Nutricional (PDF)",
            data=res_pdf,
            file_name=f"Dieta_{datetime.date.today()}.pdf",
            mime="application/pdf",
            key="btn_descarga_final"
        )

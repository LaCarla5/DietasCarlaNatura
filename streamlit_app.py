# Usar StreamLit
import streamlit as st
import pandas as pd
# Generar PDFs
from fpdf import FPDF
# Para la fecha y hora
import datetime
from io import BytesIO
# Generar graficos
import plotly.express as px

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Dietas Carla Natura", layout="wide", page_icon="🥗")

st.markdown("""
<style>
    .stButton>button { 
        background-color: #264d21; 
        color: white; 
        border-radius: 10px; 
        font-weight: bold; 
        width: 100%; 
    }
            
    .stMetric { 
        background-color: #ffffff; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 5px solid #264d21; 
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1); 
    }
    
    h1, h3 { color: #264d21; }

    [data-testid="stMetricLabel"] p {
        color: #264d21 !important;
        font-weight: bold !important;
        font-size: 1.1rem;
    }

    [data-testid="stMetricValue"] {
        color: #264d21 !important;
    }

    [data-testid="stMetricDelta"] div {
        color: #264d21 !important;
    }

    [data-testid="stMetricDelta"] svg {
        fill: #264d21 !important;
    }
            
    .overlay {
        position: fixed;
        top: 0;
        left: 21rem; 
        width: 100%;
        height: 100%;
        background-color: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(8px);
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
    }

    span[data-baseweb="tag"] {
        background-color: #264d21 !important;
    }

    div[data-baseweb="select"] {
        border-color: #264d21 !important;
    }

    .mensaje-bloqueo {
        background: white;
        padding: 3rem;
        border-radius: 20px;
        border: 2px solid #264d21;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        max-width: 600px;
        margin-top: 10%;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. CONEXIÓN Y CARGA DE DATOS ---
SHEET_ID = "14hOSakCs0yfF7WFB1nQAW0b_LqRRHkIxLzHY1u1V9PA"
URL_ING = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

@st.cache_data(ttl=5)
def cargar_datos(url):
    try:
        df = pd.read_csv(url)
        df.columns = [str(c).strip() for c in df.columns]
        return df.dropna(how='all')
    except:
        return pd.DataFrame()
def generar_pdf_planificacion(resumen_menu):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # 1. Preparar datos base
    dias_totales = list(resumen_menu.keys())
    momentos_lista = ["Desayuno", "Almuerzo", "Comida", "Merienda", "Cena"]
    platos_unicos = set()

    # --- BUCLE PARA GENERAR TABLAS (Cada 7 días) ---
    for i in range(0, len(dias_totales), 7):
        pdf.add_page() 
        dias_grupo = dias_totales[i : i + 7] 
        
        pdf.set_font("Arial", "B", 16)
        pdf.set_text_color(27, 69, 180) 
        pdf.cell(w=0, h=10, txt=f"Tabla de Dieta - CarlaNatura (Parte {int(i/7) + 1})", border=0, ln=1, align="C")
        pdf.ln(5)

        ancho_momento = 30
        ancho_dia = (277 - ancho_momento) / len(dias_grupo)

        # Cabecera
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(27, 69, 180)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(ancho_momento, 10, "Momento", 1, 0, 'C', True)
        for dia in dias_grupo:
            pdf.cell(ancho_dia, 10, dia, 1, 0, 'C', True)
        pdf.ln()

        # Filas de Momentos
        pdf.set_text_color(0, 0, 0)
        for m in momentos_lista:
            altura_fila = 28 
            y_inicio_fila = pdf.get_y()
            
            pdf.set_font("Arial", "B", 9)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(ancho_momento, altura_fila, m, 1, 0, 'C', True)
            
            for dia in dias_grupo:
                platos = resumen_menu[dia].get(m, [])
                for p in platos: platos_unicos.add(p)
                
                txt_platos = "\n".join(platos)
                x, y = pdf.get_x(), pdf.get_y()
                pdf.rect(x, y, ancho_dia, altura_fila)
                
                pdf.set_font("Arial", "B", 10)
                num_lineas = len(platos) if platos else 1
                altura_texto = num_lineas * 5 
                offset_v = (altura_fila - altura_texto) / 2
                
                pdf.set_xy(x, y_inicio_fila + max(0, offset_v))
                pdf.multi_cell(ancho_dia, 5, txt_platos.encode('latin-1', 'replace').decode('latin-1'), border=0, align='C')
                
                pdf.set_font("Arial", "", 8) 
                pdf.set_xy(x + ancho_dia, y_inicio_fila)

            # ESTA LÍNEA debe estar alineada con el 'for dia' (fuera de él)
            pdf.set_y(y_inicio_fila + altura_fila)

    # EL RETURN debe estar al final de toda la función
    return pdf.output(dest='S')

def generar_pdf(resumen_menu, df_compra):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)
    pdf.set_text_color(38, 77, 33)
    pdf.cell(190, 15, "PLAN NUTRICIONAL PERSONALIZADO", ln=True, align="C")
    pdf.set_font("Arial", "I", 10)
    pdf.cell(190, 10, f"Generado el: {datetime.date.today().strftime('%d/%m/%Y')}", ln=True, align="C")
    pdf.ln(5)

    for dia, momentos_dict in resumen_menu.items():
        pdf.set_font("Arial", "B", 12)
        pdf.set_fill_color(38, 77, 33)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(190, 9, f"  {dia.upper()}", border=1, ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        for m, platos in momentos_dict.items():
            if platos:
                pdf.set_font("Arial", "B", 10)
                pdf.cell(35, 8, f" {m}:", border="LB")
                pdf.set_font("Arial", "", 10)
                txt = ", ".join(platos).encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(155, 8, txt, border="RB")
        pdf.ln(3)

    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(38, 77, 33)
    pdf.cell(190, 10, "DETALLE DE COMPRA Y CALORÍAS", ln=True, align="C")
    pdf.ln(5)
    
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(80, 10, " Producto", 1, 0, 'L', True)
    pdf.cell(50, 10, " Cantidad", 1, 0, 'C', True)
    pdf.cell(60, 10, " Aporte Energético", 1, 1, 'C', True)

    pdf.set_font("Arial", "", 10)
    total_kcal_semana = df_compra['Kcal_Totales'].sum()
    for _, fila in df_compra.iterrows():
        pdf.cell(80, 10, f" {str(fila['Ingrediente'])[:35]}", 1)
        pdf.cell(50, 10, f" {fila['Cantidad']} {fila['Unidad']}", 1, 0, 'C')
        pdf.cell(60, 10, f" {int(fila['Kcal_Totales'])} Kcal", 1, 1, 'C')

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, f"TOTAL CALORÍAS DEL PERIODO: {int(total_kcal_semana)} Kcal", ln=True, align="R")

    output = pdf.output()
    return bytes(output) if not isinstance(output, str) else bytes(output, 'latin-1')

# --- 4. SIDEBAR (Captura de variables críticas) ---
with st.sidebar:
    st.header("👤 Perfil de Usuario")
    f_ini = st.date_input("Inicio", datetime.date.today())
    f_fin = st.date_input("Fin", datetime.date.today() + datetime.timedelta(days=6))
    st.divider()
    peso = st.number_input("Peso Actual (Kg)", min_value=0, value=0, step=1, format="%d")
    pesoDeseado = st.number_input("Peso Objetivo (Kg)", min_value=0, value=0, step=1, format="%d")
    diff = abs(peso - pesoDeseado)

    if peso > pesoDeseado:
    # Flecha hacia ABAJO (↓) para perder peso
        st.metric(label="Meta", value=f"{diff} Kg", delta=f"- {diff} Kg (Perder)")

    elif peso < pesoDeseado:
    # Flecha hacia ARRIBA (↑) para ganar peso
        st.metric(label="Meta", value=f"{diff} Kg", delta=f"+ {diff} Kg (Ganar)")


# --- 2. CONTENEDOR DINÁMICO ---
main_placeholder = st.empty()

if peso == 0 or pesoDeseado == 0:
    with main_placeholder.container():
        st.markdown("<br><br>", unsafe_allow_html=True) # Espaciado inicial
        
        # Diseño de tarjeta de bienvenida
        st.info("### 🌿 Bienvenido al Gestor de Dietas Carla Natura")
        
        col_img, col_txt = st.columns([1, 2])
        with col_img:
            # Aquí puedes poner un emoji grande o una imagen corporativa
            st.markdown("<h1 style='font-size: 150px; text-align: center;'>🥗</h1>", unsafe_allow_html=True)
        
        with col_txt:
            st.markdown("""
                ### 👋 ¡Hola! Para empezar a trabajar:
                Actualmente el panel de control está **DESACTIVADO**.
                
                **Pasos para activar:**
                1. Mira hacia el **menú de la izquierda, si no lo ves tiene este simbolo >>** ⬅️.
                2. Introduce tu **Peso Actual**.
                3. Introduce tu **Peso Objetivo**.
                
                *Una vez completado, el calendario de comidas aparecerá automáticamente.*
            """)
            st.write("---")
            st.button("Esperando datos del perfil...", disabled=True)
            
        st.stop() # Bloquea la carga de lo de abajo hasta que el peso sea > 0

# --- 6. CUERPO DE LA APP ---
st.title("🌿 Carla Natura: Gestión de Dietas")

df_recetas = cargar_datos(URL_ING)
DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
momentos = ["Desayuno", "Almuerzo", "Comida", "Merienda", "Cena"]

if not df_recetas.empty:
    c_plat, c_ing, c_gram, c_uni, c_kc = df_recetas.columns[0], df_recetas.columns[1], df_recetas.columns[2], df_recetas.columns[3], df_recetas.columns[5]

    num_dias = (f_fin - f_ini).days + 1
    for i in range(num_dias):
        fecha = f_ini + datetime.timedelta(days=i)
        st.subheader(f"📅 {DIAS_SEMANA[fecha.weekday()]} {fecha.strftime('%d/%m')}")
        cols = st.columns(5)
        for j, m in enumerate(momentos):
            key = f"sel_{fecha}_{m}"
            st.session_state[key] = cols[j].multiselect(f"{m}", sorted(df_recetas[c_plat].unique()), key=f"widget_{key}")

    st.markdown("<hr>", unsafe_allow_html=True)

    if st.button("📊 GENERAR INFORME NUTRICIONAL"):
        acumulado = []
        resumen_kcal = {}

        for i in range(num_dias):
            fecha_loop = f_ini + datetime.timedelta(days=i)
            tag = f"{DIAS_SEMANA[fecha_loop.weekday()]} {fecha_loop.strftime('%d/%m')}"
            resumen_kcal[tag] = {}
            
            for m in momentos:
                seleccionados = st.session_state.get(f"sel_{fecha_loop}_{m}", [])
                platos_formateados = []
                for plato in seleccionados:
                    ingreds = df_recetas[df_recetas[c_plat] == plato]
                    kcal_plato = 0
                    for _, row in ingreds.iterrows():
                        try:
                            g = float(str(row[c_gram]).replace(',', '.'))
                            kc100 = float(str(row[c_kc]).replace(',', '.'))
                            kc_item = (g * kc100 / 100) if str(row[c_uni]).lower() in ['g', 'ml'] else (g * kc100)
                            kcal_plato += kc_item
                            acumulado.append({
                                "Plato": plato,
                                "Ingrediente": row[c_ing], 
                                "Cantidad": g, 
                                "Unidad": row[c_uni],
                                "Kcal_Totales": kc_item
                            })
                        except: pass
                    platos_formateados.append(f"{plato} ({int(kcal_plato)} Kcal)")
                resumen_kcal[tag][m] = platos_formateados

        if acumulado:
            df_compra = pd.DataFrame(acumulado).groupby(['Ingrediente', 'Unidad']).agg({
                'Cantidad': 'sum',
                'Kcal_Totales': 'sum'
            }).reset_index()
            
            st.session_state["df_final"] = df_compra
            st.session_state["resumen_kcal"] = resumen_kcal
            st.session_state["generar_pdf"] = generar_pdf(resumen_kcal, df_compra)
            st.session_state["pdf_planificacion"] = generar_pdf_planificacion(resumen_kcal)
            st.success("✅ ¡Informe listo!")

    if "df_final" in st.session_state:
        st.divider()
        st.subheader("🛒 Carrito de la Compra y Análisis Visual")
        
        # Recuperamos el DataFrame original (sin agrupar todavía por ingrediente solo)
        df_compra_con_platos = pd.DataFrame(acumulado) # 'acumulado' viene de la lógica del botón arriba

        # Creamos dos pestañas para organizar la vista
        tab1, tab2 = st.tabs(["📊 Gráficos Interactivos", "📋 Lista de Compra Detallada"])

        with tab1:
            st.markdown("### Desglose de Calorías por Plato e Ingrediente")
            
            # --- NUEVO GRÁFICO 1: Barras Apiladas (Stacked Bar Chart) ---
            # Este gráfico muestra qué plato es más calórico y qué ingredientes lo componen
            fig_bar_stacked = px.bar(
                df_compra_con_platos, 
                x='Kcal_Totales', 
                y='Plato', 
                color='Ingrediente', # El color divide la barra por ingrediente
                orientation='h',
                title="Calorías Totales por Plato (Desglosado por Ingrediente)",
                labels={'Kcal_Totales': 'Calorías', 'Plato': 'Plato Seleccionado'},
                hover_data={'Cantidad': True, 'Unidad': True, 'Kcal_Totales': ':.1f'} # Datos al pasar el ratón
            )
            # Ordenar las barras para que el plato más calórico esté arriba
            fig_bar_stacked.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
            st.plotly_chart(fig_bar_stacked, use_container_width=True)


            # --- NUEVO GRÁFICO 2: Gráfico de Sol (Sunburst Chart) ---
            # Este gráfico es perfecto para ver jerarquías: Plato -> Ingrediente
            st.markdown("---")
            st.markdown("### Jerarquía de Consumo: De Plato a Ingrediente")
            
            fig_sunburst = px.sunburst(
                df_compra_con_platos,
                path=['Plato', 'Ingrediente'], # Define la jerarquía
                values='Kcal_Totales',
                title="Distribución Jerárquica de Calorías",
                color='Kcal_Totales', # Color según calorías para destacar lo pesado
                color_continuous_scale='RdYlGn_r', # Rojo (alto) a Verde (bajo), invertido
                hover_data={'Kcal_Totales': ':.1f Kcal'}
            )
            fig_sunburst.update_traces(textinfo="label+percent entry")
            st.plotly_chart(fig_sunburst, use_container_width=True)

        with tab2:
            # Mostramos la tabla de compra agrupada solo por ingrediente (como antes)
            st.subheader("Lista de la Compra Consolidada")
            df_compra_agrupada = df_compra_con_platos.groupby(['Ingrediente', 'Unidad']).agg({
                'Cantidad': 'sum',
                'Kcal_Totales': 'sum'
            }).reset_index()
            
            st.dataframe(df_compra_agrupada.style.format({"Cantidad": "{:.2f}", "Kcal_Totales": "{:.0f}"}), use_container_width=True)
            
            # Botón de descarga PDF
            st.download_button(
                label="🛒 Lista de la compra",
                data=st.session_state["generar_pdf"],
                file_name=f"Dieta_CarlaNatura_{datetime.date.today()}.pdf",
                mime="application/pdf"
            )
            st.download_button(
                label="📥 Descargar Dieta Semanal",
                data=st.session_state["planificacion_pdf"], 
                file_name=f"Dieta_CarlaNatura_{datetime.date.today()}.pdf",
                mime="application/pdf"
            )
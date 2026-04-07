# Stream lit
import streamlit as st
import pandas as pd
# Generacion de PDF
from fpdf import FPDF
# Tiempo y hora (Calendario)
import datetime

# Configuracion de pagina y estilos
st.set_page_config(page_title="Dietas Carla Natura", layout="wide", page_icon="⚜️")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { 
        background-color: #264d21; 
        color: white; 
        border-radius: 10px; 
        height: 3em; 
        width: 100%;
        font-weight: bold;
    }
    .stMetric { 
        background-color: #ffffff; 
        padding: 15px; 
        border-radius: 10px; 
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1); 
        border-left: 5px solid #264d21;
    }
    .stMetric div {
        color: #264d21 !important;
    }
    h1 { color: #264d21; text-align: center; }
    h3 { color: #264d21; border-bottom: 2px solid #264d21; padding-bottom: 5px; margin-top: 30px; }
    hr { border-top: 2px solid #264d21 !important; }
    
    span[data-baseweb="tag"] {
        background-color: #264d21 !important;
    }
    div[data-baseweb="select"] {
        border-color: #264d21 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Conexion con nuestros Excel (BBDD)
SHEET_ID = "14hOSakCs0yfF7WFB1nQAW0b_LqRRHkIxLzHY1u1V9PA"
URL_ING = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
GID_PLANTILLAS = "2040007005" 
URL_PLAN = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_PLANTILLAS}"

@st.cache_data(ttl=5)
def cargar_datos(url):
    try:
        df = pd.read_csv(url)
        df.columns = [str(c).strip() for c in df.columns]
        return df.dropna(how='all')
    except:
        return pd.DataFrame()

# --- FUNCIÓN PDF CORREGIDA (AHORA ACEPTA 3 ARGUMENTOS) ---
def generar_pdf(pesoDeseado, resumen_menu, df_compra):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- PÁGINA 1: MENÚ ---
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(38, 77, 33) 
    pdf.cell(w=200, h=10, txt="Dietas Semanales Carla Natura", border=0, ln=1, align="C")
    pdf.ln(10)
    
    for dia, momentos_dict in resumen_menu.items():
        pdf.set_font("Arial", "B", 11)
        pdf.set_fill_color(38, 77, 33) 
        pdf.set_text_color(255, 255, 255)
        pdf.cell(190, 8, f" {dia}", 1, 1, 'L', True)
        
        pdf.set_font("Arial", "", 9)
        pdf.set_text_color(0, 0, 0)
        for m, platos in momentos_dict.items():
            if platos:
                # Limpiamos el texto de caracteres que no sean latin-1 (como el emoji de la siringa o scout)
                txt_platos = ", ".join(platos).encode('latin-1', 'replace').decode('latin-1')
                pdf.set_font("Arial", "B", 9)
                pdf.cell(40, 6, f" {m}:", border="LTB", ln=0)
                pdf.set_font("Arial", "", 9)
                pdf.multi_cell(150, 6, txt_platos, border="RTB")
        pdf.ln(2)

    # --- PÁGINA 2: COMPRA ---
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(38, 77, 33)
    pdf.cell(200, 10, "LISTA DE LA COMPRA FINAL", ln=True, align="C")
    pdf.ln(5)
    
    pdf.set_font("Arial", "", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(200, 10, f"Objetivo de Peso: {pesoDeseado} Kg", ln=True)
    pdf.ln(5)
    
    pdf.set_fill_color(38, 77, 33) 
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(100, 10, " Ingrediente", 1, 0, 'L', True)
    pdf.cell(90, 10, " Cantidad Total", 1, 1, 'L', True)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 10)
    
    for _, fila in df_compra.iterrows():
        ing = str(fila['Ingrediente']).encode('latin-1', 'replace').decode('latin-1')
        cant = str(fila['Cantidad'])
        uni = str(fila['Unidad']).encode('latin-1', 'replace').decode('latin-1')
        
        pdf.cell(100, 10, f" {ing}", 1, 0, 'L')
        pdf.cell(90, 10, f" {cant} {uni}", 1, 1, 'L')

    pdf_output = pdf.output()
    
    # Si la salida es un string (versiones antiguas), lo pasamos a bytes
    if isinstance(pdf_output, str):
        return bytes(pdf_output, 'latin-1')
    
    # Si ya son bytes o bytearray, nos aseguramos de devolver el tipo 'bytes'
    return bytes(pdf_output)

# --- LÓGICA DE DATOS ---
df_recetas = cargar_datos(URL_ING)
df_plantillas = cargar_datos(URL_PLAN)
DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
momentos = ["Desayuno", "Almuerzo", "Comida", "Merienda", "Cena"]

with st.sidebar:
    st.header("👥 Peso y Dias")
    f_ini = st.date_input("Fecha inicio", datetime.date.today())
    f_fin = st.date_input("Fecha fin", datetime.date.today() + datetime.timedelta(days=6))
    st.divider()
    peso = st.number_input("Peso Actual (Kg)", 0, 500, 0)
    pesoDeseado = st.number_input("Peso Deseado (Kg)", 0, 500, 0)

    diferenciaPeso = abs(peso - pesoDeseado)
    label_metric = "Peso a perder" if peso > pesoDeseado else "Peso a ganar"
    st.metric(label=label_metric, value=f"{diferenciaPeso} Kg")

st.title("Dietas Carla Natura")

if not df_recetas.empty:
    c_plat = df_recetas.columns[0]
    c_ing = df_recetas.columns[1]
    c_gram = df_recetas.columns[2]
    c_uni = df_recetas.columns[3]
    c_kc = df_recetas.columns[5]
    c_obj = df_recetas.columns[6]

    if not df_plantillas.empty:
        with st.expander("📂 Cargar Dietas desde Plantilla"):
            nombres_p = ["Ninguna"] + list(df_plantillas["Nombre_Plantilla"].unique())
            plantilla_sel = st.selectbox("Selecciona plantilla:", nombres_p)
            if st.button("Aplicar"):
                datos_p = df_plantillas[df_plantillas["Nombre_Plantilla"] == plantilla_sel]
                for i in range((f_fin - f_ini).days + 1):
                    fecha_p = f_ini + datetime.timedelta(days=i)
                    for m in momentos:
                        matches = datos_p[(datos_p["Dia_Relativo"] == (i+1)) & (datos_p["Momento"] == m)]
                        if not matches.empty:
                            st.session_state[f"sel_{fecha_p}_{m}"] = matches["Plato"].tolist()
                st.rerun()

    platos_opciones = sorted([str(p) for p in df_recetas[c_plat].dropna().unique()])
    num_dias = (f_fin - f_ini).days + 1
    for i in range(num_dias):
        fecha = f_ini + datetime.timedelta(days=i)
        st.subheader(f"📅 {DIAS_SEMANA[fecha.weekday()]} {fecha.strftime('%d/%m')}")
        cols = st.columns(len(momentos))
        for j, m in enumerate(momentos):
            key = f"sel_{fecha}_{m}"
            cols[j].multiselect(f"{m}", platos_opciones, key=key)

    st.markdown("<hr>", unsafe_allow_html=True)

    if st.button("📦 PREPARAR LISTA DE COMPRA"):
        if pesoDeseado <= 0 or peso <= 0:
            st.error("⚠️ Error: Introduce pesos válidos.")
        else:
            acumulado_ingredientes = []
            resumen_dieta_kcal = {}
            platos_seleccionados_total = 0

            for i in range(num_dias):
                fecha_loop = f_ini + datetime.timedelta(days=i)
                tag_dia = f"{DIAS_SEMANA[fecha_loop.weekday()]} {fecha_loop.strftime('%d/%m')}"
                resumen_dieta_kcal[tag_dia] = {}

                for m in momentos:
                    seleccionados = st.session_state.get(f"sel_{fecha_loop}_{m}", [])
                    platos_seleccionados_total += len(seleccionados)
                    platos_con_kcal = []
                    
                    for plato in seleccionados:
                        ingreds = df_recetas[df_recetas[c_plat] == plato]
                        kcal_acumulada_plato = 0
                        for _, row in ingreds.iterrows():
                            try: 
                                g_p = float(str(row[c_gram]).replace(',', '.').strip())
                                kc_100 = float(str(row[c_kc]).replace(',', '.').strip())
                                if str(row[c_uni]).lower() in ['g', 'ml']:
                                    kcal_ingrediente = (g_p * kc_100) / 100
                                else:
                                    kcal_ingrediente = g_p * kc_100
                            except: kcal_ingrediente = 0
                            
                            kcal_acumulada_plato += kcal_ingrediente
                            acumulado_ingredientes.append({"Ingrediente": row[c_ing], "Cantidad": g_p, "Unidad": row[c_uni]})
                        
                        platos_con_kcal.append(f"{plato} ({int(kcal_acumulada_plato)} Kcal)")
                    resumen_dieta_kcal[tag_dia][m] = platos_con_kcal
            
            if platos_seleccionados_total == 0:
                st.error("⚠️ Error: No has seleccionado ningún plato.")
            else:
                df_compra = pd.DataFrame(acumulado_ingredientes)
                df_final = df_compra.groupby(['Ingrediente', 'Unidad'])['Cantidad'].sum().reset_index()
                df_final = df_final[['Ingrediente', 'Cantidad', 'Unidad']]
                df_final['Cantidad'] = df_final['Cantidad'].round(2)
                
                st.session_state["df_compra"] = df_final
                st.session_state["resumen_menu"] = resumen_dieta_kcal
                
                # GENERAR PDF Y GUARDAR
                st.session_state["pdf_data"] = generar_pdf(pesoDeseado, resumen_dieta_kcal, df_final)
                st.success("✅ Dieta calculada con éxito.")

    if "pdf_data" in st.session_state:
        st.subheader("📋 Tu Plan Nutricional")
        st.dataframe(st.session_state["df_compra"], use_container_width=True)
        st.download_button(
            label="📥 Descarga tu dieta adaptada (PDF)",
            data=st.session_state["pdf_data"],
            file_name=f"dieta_CarlaNatura_{datetime.date.today()}.pdf",
            mime="application/pdf"
        )
import streamlit as st
import pandas as pd
from fpdf import FPDF
import datetime
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Dietas Carla Natura", layout="wide", page_icon="🥗")

# Estilos CSS (Verde Carla Natura)
st.markdown("""
    <style>
    .stButton>button { background-color: #264d21; color: white; border-radius: 10px; font-weight: bold; width: 100%; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border-left: 5px solid #264d21; }
    h1, h3 { color: #264d21; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN Y DATOS ---
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

# --- FUNCIÓN PDF MEJORADA ---
def generar_pdf(pesoDeseado, resumen_menu, df_compra):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # PÁGINA 1: MENÚ SEMANAL
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
        pdf.set_font("Arial", "", 10)
        for m, platos in momentos_dict.items():
            if platos:
                # Escribimos el momento (Desayuno, etc) en negrita
                pdf.set_font("Arial", "B", 10)
                pdf.cell(35, 8, f" {m}:", border="LB")
                # Escribimos los platos en normal
                pdf.set_font("Arial", "", 10)
                txt = ", ".join(platos).encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(155, 8, txt, border="RB")
        pdf.ln(3)

    # PÁGINA 2: LISTA DE COMPRA Y NUTRICIÓN
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(38, 77, 33)
    pdf.cell(190, 10, "DETALLE DE COMPRA Y CALORÍAS", ln=True, align="C")
    pdf.ln(5)
    
    # Tabla de compra
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

# --- CARGA DE DATOS ---
df_recetas = cargar_datos(URL_ING)
DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
momentos = ["Desayuno", "Almuerzo", "Comida", "Merienda", "Cena"]

# --- SIDEBAR ---
with st.sidebar:
    st.header("👤 Perfil de Usuario")
    f_ini = st.date_input("Inicio", datetime.date.today())
    f_fin = st.date_input("Fin", datetime.date.today() + datetime.timedelta(days=6))
    peso = st.number_input("Peso Actual (Kg)", value=70)
    pesoDeseado = st.number_input("Peso Objetivo (Kg)", value=65)
    diff = abs(peso - pesoDeseado)
    st.metric("Meta", f"{diff} Kg", "Perder" if peso > pesoDeseado else "Ganar")

st.title("🌿 Carla Natura: Gestión de Dietas")

if not df_recetas.empty:
    c_plat, c_ing, c_gram, c_uni, c_kc = df_recetas.columns[0], df_recetas.columns[1], df_recetas.columns[2], df_recetas.columns[3], df_recetas.columns[5]

    # --- CALENDARIO ---
    num_dias = (f_fin - f_ini).days + 1
    for i in range(num_dias):
        fecha = f_ini + datetime.timedelta(days=i)
        st.subheader(f"📅 {DIAS_SEMANA[fecha.weekday()]} {fecha.strftime('%d/%m')}")
        cols = st.columns(5)
        for j, m in enumerate(momentos):
            st.session_state[f"sel_{fecha}_{m}"] = cols[j].multiselect(f"{m}", sorted(df_recetas[c_plat].unique()), key=f"key_{fecha}_{m}")

    # --- CÁLCULOS ---
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
                            # Lógica: Si es g/ml divide por 100, si es ud multiplica directo
                            kc_item = (g * kc100 / 100) if str(row[c_uni]).lower() in ['g', 'ml'] else (g * kc100)
                            kcal_plato += kc_item
                            acumulado.append({
                                "Ingrediente": row[c_ing], 
                                "Cantidad": g, 
                                "Unidad": row[c_uni],
                                "Kcal_Totales": kc_item
                            })
                        except: pass
                    platos_formateados.append(f"{plato} ({int(kcal_plato)} Kcal)")
                resumen_kcal[tag][m] = platos_formateados

        if acumulado:
            # Agrupamos por ingrediente sumando CANTIDAD y KCAL
            df_compra = pd.DataFrame(acumulado).groupby(['Ingrediente', 'Unidad']).agg({
                'Cantidad': 'sum',
                'Kcal_Totales': 'sum'
            }).reset_index()
            
            st.session_state["df_final"] = df_compra
            st.session_state["resumen_kcal"] = resumen_kcal
            st.session_state["pdf_bytes"] = generar_pdf(pesoDeseado, resumen_kcal, df_compra)
            st.success("✅ ¡Informe listo!")

    # --- RESULTADOS ---
    if "df_final" in st.session_state:
        st.divider()
        st.subheader("🛒 Carrito de la Compra Nutricional")
        st.dataframe(st.session_state["df_final"].style.format({"Cantidad": "{:.2f}", "Kcal_Totales": "{:.0f}"}), use_container_width=True)
        
        st.download_button(
            label="📥 Descargar Dieta PDF Profesional",
            data=st.session_state["pdf_bytes"],
            file_name=f"Dieta_CarlaNatura_{datetime.date.today()}.pdf",
            mime="application/pdf"
        )
import streamlit as st
import pandas as pd
from fpdf import FPDF
import datetime
from io import BytesIO

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

def generar_pdf(pesoDeseado, resumen_menu, df_compra):
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
            st.session_state["pdf_bytes"] = generar_pdf(pesoDeseado, resumen_kcal, df_compra)
            st.success("✅ ¡Informe listo!")

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
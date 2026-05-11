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
# Inicializar las llaves para evitar KeyError
if "planificacion_pdf" not in st.session_state:
    st.session_state["planificacion_pdf"] = None
if "pdf_bytes" not in st.session_state:
    st.session_state["pdf_bytes"] = None
if "df_final" not in st.session_state:
    st.session_state["df_final"] = None

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
    output = pdf.output(dest='S')
    if isinstance(output, str):
        return bytes(output, 'latin-1')
    return bytes(output)

def generar_pdf(resumen_menu, df_compra):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- PÁGINA 1: PLANIFICACIÓN ---
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)
    pdf.set_text_color(38, 77, 33)
    pdf.cell(190, 15, "PLAN NUTRICIONAL PERSONALIZADO", ln=True, align="C")
    pdf.set_font("Arial", "I", 10)
    pdf.cell(190, 10, f"Generado el: {datetime.date.today().strftime('%d/%m/%Y')}", ln=True, align="C")
    pdf.ln(5)

    for dia, momentos_dict in resumen_menu.items():
        # Cabecera del día (Verde)
        pdf.set_font("Arial", "B", 12)
        pdf.set_fill_color(38, 77, 33)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(190, 9, f"  {dia.upper()}", border=1, ln=True, fill=True)
        
        pdf.set_text_color(0, 0, 0)
        # Recorremos cada momento
        for m in ["Desayuno", "Almuerzo", "Comida", "Merienda", "Cena"]:
            platos = momentos_dict.get(m, [])
            if platos:
                # 1. Guardamos la posición Y actual
                y_inicio = pdf.get_y()
                
                # 2. Escribimos el Momento (Columna izquierda)
                pdf.set_font("Arial", "B", 10)
                # IMPORTANTE: Usamos multi_cell pero sin ln=True para controlar el salto manualmente
                pdf.multi_cell(40, 10, f"{m}:", border='L', align='L')
                
                # 3. Nos movemos a la derecha del momento para los platos
                pdf.set_xy(pdf.get_x() + 50, y_inicio) 
                
                # 4. Escribimos los Platos (Columna derecha)
                pdf.set_font("Arial", "", 10)
                txt_platos = ", ".join(platos).encode('latin-1', 'replace').decode('latin-1')
                # Aquí usamos ln=True para que el SIGUIENTE momento aparezca debajo
                pdf.multi_cell(140, 10, txt_platos, border='R', align='L', ln=True)
                
                # 5. Dibujamos una línea sutil de separación inferior
                pdf.line(10, pdf.get_y(), 200, pdf.get_y())

        pdf.ln(5) # Espacio extra tras cerrar el día

    # --- PÁGINA 2: LISTA DE COMPRA ---
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(38, 77, 33)
    pdf.cell(190, 10, "DETALLE DE COMPRA Y CALORÍAS", ln=True, align="C")
    pdf.ln(5)
    
    # Cabecera tabla compra
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(90, 10, " Producto", 1, 0, 'L', True)
    pdf.cell(40, 10, " Cantidad", 1, 0, 'C', True)
    pdf.cell(60, 10, " Energía", 1, 1, 'C', True)

    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(0, 0, 0)
    for _, fila in df_compra.iterrows():
        # Guardamos Y para que la fila sea uniforme
        y_fila = pdf.get_y()
        pdf.multi_cell(90, 10, f" {str(fila['Ingrediente'])[:45]}", border=1)
        pdf.set_xy(100, y_fila) # 10 (margen) + 90 (ancho)
        pdf.cell(40, 10, f"{fila['Cantidad']:.2f} {fila['Unidad']}", 1, 0, 'C')
        pdf.cell(60, 10, f"{int(fila['Kcal_Totales'])} Kcal", 1, 1, 'C')

    # Retorno de bytes seguro
    output = pdf.output(dest='S')
    if isinstance(output, str):
        return bytes(output, 'latin-1')
    return bytes(output)

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

    # --- 1. BOTÓN DE GENERAR ---
    if st.button("📊 GENERAR INFORME NUTRICIONAL"):
        acumulado = []
        resumen_kcal = {}

        # 1. Recorremos los días seleccionados
        for i in range(num_dias):
            fecha_loop = f_ini + datetime.timedelta(days=i)
            tag = f"{DIAS_SEMANA[fecha_loop.weekday()]} {fecha_loop.strftime('%d/%m')}"
            resumen_kcal[tag] = {}
            
            # 2. Recorremos los momentos (Desayuno, Comida...)
            for m in momentos:
                key = f"sel_{fecha_loop}_{m}"
                seleccionados = st.session_state.get(key, [])
                platos_formateados = []
                
                for plato in seleccionados:
                    # Buscamos los ingredientes de ese plato en el Excel
                    ingreds = df_recetas[df_recetas[c_plat] == plato]
                    kcal_plato = 0
                    
                    for _, row in ingreds.iterrows():
                        try:
                            # Limpieza de números (por si vienen con coma del Excel)
                            g = float(str(row[c_gram]).replace(',', '.'))
                            kc100 = float(str(row[c_kc]).replace(',', '.'))
                            
                            # Lógica de cálculo: si es g/ml dividimos por 100, si es 'unidad' multiplicamos directo
                            if str(row[c_uni]).lower() in ['g', 'ml']:
                                kc_item = (g * kc100 / 100)
                            else:
                                kc_item = (g * kc100)
                                
                            kcal_plato += kc_item
                            
                            # Guardamos en la lista para la compra y los gráficos
                            acumulado.append({
                                "Plato": plato,
                                "Ingrediente": row[c_ing], 
                                "Cantidad": g, 
                                "Unidad": row[c_uni],
                                "Kcal_Totales": kc_item
                            })
                        except:
                            continue
                    
                    platos_formateados.append(f"{plato} ({int(kcal_plato)} Kcal)")
                
                resumen_kcal[tag][m] = platos_formateados

        # 3. Solo si hay datos, generamos los resultados
        if acumulado:
            # Agrupamos para la tabla de compra consolidada
            df_compra = pd.DataFrame(acumulado).groupby(['Ingrediente', 'Unidad']).agg({
                'Cantidad': 'sum', 
                'Kcal_Totales': 'sum'
            }).reset_index()
            
            # --- GUARDAMOS TODO EN EL ESTADO (VITAL PARA QUE NO SE PIERDA) ---
            st.session_state["df_final"] = df_compra
            st.session_state["acumulado"] = acumulado
            st.session_state["resumen_kcal"] = resumen_kcal
            
            # Generamos los PDFs usando las funciones que ya tienes arriba
            st.session_state["pdf_bytes"] = generar_pdf(resumen_kcal, df_compra)
            st.session_state["planificacion_pdf"] = generar_pdf_planificacion(resumen_kcal)
            
            st.success("✅ ¡Informe generado con éxito! Baja para ver los resultados.")
            st.rerun() # Refresca la página para mostrar los gráficos
        else:
            st.warning("⚠️ No has seleccionado ningún plato en el calendario.")

# --- SECCIÓN DE RESULTADOS Y DESCARGAS ---
# Extraemos todo con .get() para que NUNCA de KeyError
datos_acumulado = st.session_state.get("acumulado", None)
datos_lista_compra = st.session_state.get("pdf_bytes", None)
datos_planificacion = st.session_state.get("planificacion_pdf", None)
hay_datos_finales = st.session_state.get("df_final", None)

# Solo entramos si realmente se ha pulsado el botón de generar
if hay_datos_finales is not None and datos_acumulado is not None:
    st.divider()
    st.header("📊 Análisis de tu Dieta Personalizada")
    
    # Creamos el DataFrame desde la variable segura que sacamos arriba
    df_compra_con_platos = pd.DataFrame(datos_acumulado)
    
    # Pestañas para organizar la info
    tab1, tab2 = st.tabs(["📈 Gráficos de Energía", "📋 Lista de Compra"])

    with tab1:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("### Calorías por Plato e Ingrediente")
            fig_bar = px.bar(
                df_compra_con_platos, 
                x='Kcal_Totales', y='Plato', color='Ingrediente',
                orientation='h', title="Desglose Calórico",
                color_discrete_sequence=px.colors.qualitative.Dark2
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col_b:
            st.markdown("### Jerarquía de la Dieta")
            fig_sun = px.sunburst(
                df_compra_con_platos, path=['Plato', 'Ingrediente'], values='Kcal_Totales',
                color='Kcal_Totales', color_continuous_scale='Greens'
            )
            st.plotly_chart(fig_sun, use_container_width=True)

    with tab2:
        st.subheader("🛒 Carrito de la Compra Consolidado")
        # Usamos la variable segura hay_datos_finales
        st.dataframe(hay_datos_finales.style.format({"Cantidad": "{:.2f}", "Kcal_Totales": "{:.0f}"}), use_container_width=True)
        
        st.markdown("### 📥 Descargas Disponibles")
        c1, c2 = st.columns(2)
        
        with c1:
            if datos_lista_compra:
                st.download_button(
                    label="🛒 Descargar Lista de la Compra",
                    data=datos_lista_compra,
                    file_name=f"Lista_Compra_{datetime.date.today()}.pdf",
                    mime="application/pdf",
                    key="btn_compra_seguro_v2"
                )
        
        with c2:
            if datos_planificacion:
                st.download_button(
                    label="📅 Descargar Tabla Semanal",
                    data=datos_planificacion, 
                    file_name=f"Tabla_Semanal_{datetime.date.today()}.pdf",
                    mime="application/pdf",
                    key="btn_tabla_seguro_v2"
                )
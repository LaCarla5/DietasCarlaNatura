🌿 Carla Natura: Gestión de Dietas Inteligentes
Carla Natura es una aplicación web interactiva desarrollada con Streamlit diseñada para nutricionistas y profesionales de la salud. Permite planificar dietas semanales, calcular automáticamente el aporte calórico de cada plato y generar una lista de la compra detallada con el impacto energético de cada ingrediente.

✨ Características Principales
📅 Planificador Semanal: Selecciona platos para cada momento del día (Desayuno, Almuerzo, Comida, Merienda y Cena).

📊 Cálculo Nutricional Automático: Calcula las Kcal totales de cada plato basándose en una base de datos externa (Google Sheets).

🛒 Lista de Compra Inteligente: Agrupa ingredientes y muestra la cantidad total necesaria junto con el aporte energético acumulado.

📥 Generación de Informes PDF: Exporta un documento profesional con el menú semanal y el detalle de la compra para el paciente.

⚖️ Control de Objetivos: Seguimiento visual de la meta de peso (ganar o perder).

🚀 Instalación y Configuración
1. Clonar el repositorio
Para obtener una copia local del proyecto, ejecuta:

Bash
git clone https://github.com/tu-usuario/carla-natura.git
cd carla-natura
2. Crear un entorno virtual (Recomendado)
Es aconsejable usar un entorno virtual para mantener las dependencias aisladas:

Bash
python -m venv venv
Para activarlo:

En Windows:

Bash
venv\Scripts\activate
En Mac/Linux:

Bash
source venv/bin/activate
3. Instalar dependencias
Instala todas las librerías necesarias mediante el archivo requirements.txt:

Bash
pip install -r requirements.txt
🛠️ Requisitos Técnicos
El archivo requirements.txt incluye las siguientes librerías fundamentales:

Streamlit: Para la interfaz de usuario web.

Pandas: Para la gestión y cálculo de las tablas nutricionales.

fpdf2: Para la generación de los informes PDF profesionales.

📊 Estructura de Datos (Excel/Google Sheets)
Para que la aplicación funcione correctamente, la hoja de cálculo vinculada debe respetar el siguiente orden de columnas:

Plato: Nombre de la receta.

Ingrediente: Nombre del componente.

Gramos_Persona: Cantidad asignada por ración.

Unidad: Medida (g, ml, ud).

Categoría: Clasificación del plato.

KiloCalorias: Valor energético (por cada 100g/ml o por unidad).

🖥️ Uso de la Aplicación
Para lanzar la aplicación en tu navegador local, ejecuta:

Bash
streamlit run streamlit_app.py
Pasos para generar una dieta:
Configura el perfil: Introduce el peso actual y objetivo en la barra lateral.

Define el periodo: Selecciona la fecha de inicio y fin del plan nutricional.

Planifica el menú: Elige los platos deseados en los selectores del calendario.

Calcula: Haz clic en el botón "Generar Informe Nutricional".

Exporta: Revisa la tabla de compra en pantalla y descarga el PDF profesional.

Generado con ❤️ para Carla Natura.
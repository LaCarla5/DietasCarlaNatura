# 🌿 Carla Natura: Gestión de Dietas Inteligentes

Carla Natura es una aplicación web interactiva desarrollada con **Streamlit** diseñada para nutricionistas y profesionales de la salud. Permite planificar dietas semanales, calcular automáticamente el aporte calórico de cada plato y generar una lista de la compra detallada con el impacto energético de cada ingrediente.

## ✨ Características Principales

- **📅 Planificador Semanal:** Selecciona platos para cada momento del día (Desayuno, Almuerzo, Comida, Merienda y Cena).
- **📊 Cálculo Nutricional Automático:** Calcula las Kcal totales de cada plato basándose en una base de datos externa (Google Sheets).
- **🛒 Lista de Compra Inteligente:** Agrupa ingredientes y muestra la cantidad total necesaria junto con el aporte energético acumulado.
- **📥 Generación de Informes PDF:** Exporta un documento profesional con el menú semanal y el detalle de la compra para el paciente.
- **⚖️ Control de Objetivos:** Seguimiento visual de la meta de peso (ganar o perder).

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone [https://github.com/tu-usuario/carla-natura.git](https://github.com/tu-usuario/carla-natura.git)
cd carla-natura

### 2. Crear un entorno virtual (Recomendado)
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Mac/Linux:
source venv/bin/activate

### 3. Instalar dependencias
#### Utiliza el archivo requirements.txt incluido en el proyecto:
pip install -r requirements.txt

### 🛠️ Requisitos Técnicos
El archivo requirements.txt debe contener al menos las siguientes librerías:

streamlit: Para la interfaz de usuario.

pandas: Para el procesamiento de datos.

fpdf2: Para la generación de documentos PDF.

### 📊 Estructura de Datos (Excel/Google Sheets)
Para que la aplicación funcione, la hoja de cálculo vinculada debe tener las siguientes columnas en el orden especificado:

Plato: Nombre del plato.

Ingrediente: Nombre del ingrediente.

Gramos_Persona: Cantidad base.

Unidad: (g, ml, ud).

Categoría: (Opcional).

KiloCalorias: Valor energético por cada 100g/ml o por unidad.

🖥️ Uso de la Aplicación
Para lanzar la aplicación localmente, ejecuta:

Bash
streamlit run streamlit_app.py
Configura el perfil del usuario (peso actual y objetivo) en la barra lateral.

Selecciona las fechas del plan nutricional.

Elige los platos en el calendario central.

Haz clic en "Generar Informe Nutricional".

Revisa la tabla de compra y descarga el PDF profesional.

Generado con ❤️ para Carla Natura.
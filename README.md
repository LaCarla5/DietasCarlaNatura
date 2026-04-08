# 🌿 Carla Natura: Gestión de Dietas Inteligentes

**Carla Natura** es una aplicación web interactiva desarrollada con [Streamlit](https://streamlit.io/) diseñada para nutricionistas y profesionales de la salud. Permite planificar dietas semanales, calcular automáticamente el aporte calórico de cada plato y generar una lista de la compra detallada con el impacto energético de cada ingrediente.

---

## ✨ Características Principales

* **📅 Planificador Semanal:** Selecciona platos para cada momento del día (Desayuno, Almuerzo, Comida, Merienda y Cena).
* **📊 Cálculo Nutricional Automático:** Calcula las Kcal totales de cada plato basándose en una base de datos externa vinculada a Google Sheets.
* **🛒 Lista de Compra Inteligente:** Agrupa ingredientes idénticos y muestra la cantidad total necesaria junto con el aporte energético (Kcal) acumulado por cada producto.
* **📥 Generación de Informes PDF:** Exporta un documento profesional con el menú semanal detallado y la lista de la compra para el paciente.
* **⚖️ Control de Objetivos:** Seguimiento visual de la meta de peso (ganar o perder) mediante métricas dinámicas.

---

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio
Para obtener una copia local del proyecto en tu máquina o servidor:

```bash
git clone [https://github.com/tu-usuario/carla-natura.git](https://github.com/tu-usuario/carla-natura.git)
cd carla-natura
```

---

### 2. Crear un entorno virtual (Recomendado)
Es aconsejable usar un entorno virtual para evitar conflictos entre librerías:

```bash
python -m venv venv
```

**Activar el entorno:**

* ** Windows: 
```bash
venv\Scripts\activate
```
* **Mac/Linux: 
```bash
source venv/bin/activate
```

### 3. Instalar dependencias
Instala todas las librerías necesarias utilizando el archivo de requisitos incluido:

```bash
pip install -r requirements.txt
```

---

### 🛠️ Requisitos Técnicos
El archivo requirements.txt debe contener las siguientes librerías para garantizar el correcto funcionamiento:

```bash
streamlit
pandas
fpdf2
```

---

### 📊 Estructura de la Base de Datos
La aplicación consume datos de un archivo CSV o Google Sheets. Para que los cálculos sean correctos, las columnas deben seguir este orden:

```bash
Plato	Ingrediente	| Gramos_Persona	| Unidad | Categoría	| KiloCaloria (100g)	| Objetivo
Choque de Puré Verde	| Calabacín	| 250	| g	| Cena	| 17	| Adelgazar
Choque de Puré Verde	| Puerros	| 50	| g	| Cena	| 61	| Adelgazar
Choque de Puré Verde	| Quesito light| 	1	| ud	| Cena	| 25	| Adelgazar
```
---

### 🖥️ Uso de la Aplicación
Para lanzar la aplicación localmente, ejecuta el siguiente comando en tu terminal:

```bash
streamlit run streamlit_app.py
```

---

## ✨ Guía de usuario:

* **📅 Perfil:** Introduce el peso actual y el peso deseado en la barra lateral.
* **📊 Calendario:** Navega por los días de la semana y usa los selectores para añadir platos a cada comida.
* **🛒 Cálculo:** Haz clic en el botón "📊 GENERAR INFORME NUTRICIONAL".
* **📥 Resumen:** Revisa en pantalla las Kcal totales por ingrediente y por plato.
* **⚖️ PDF:** Descarga el informe final listo para enviar al cliente.



 



 

 

 


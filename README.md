# Databento Futures Symbols Guide

## ⚡ Instalación Rápida

```bash
# 1. Clonar el proyecto
git clone https://github.com/vicenteh2o/databento-matplotlib.git
cd databento-matplotlib

# 2. Crear y activar entorno virtual
python3 -m venv .venv
source .venv/bin/activate  # En macOS/Linux
# .venv\Scripts\activate   # En Windows

# 3. Instalar todas las dependencias
pip install -r requirements.txt

# 4. Crear archivo .env con tu API key
echo "DATABENTO_API_KEY=tu-api-key-aqui" > .env

# 5. Ejecutar script principal
python monthly_projection_2026.py
```

---

## 🔧 Configuración Inicial

### 1. Configurar Entorno Virtual

Para ejecutar este proyecto correctamente, sigue estos pasos:

1. **Clonar o descargar el proyecto**:

```bash
cd /ruta/a/tu/proyecto/databento
```

2. **Crear entorno virtual**:

```bash
python3 -m venv .venv
```

3. **Activar el entorno virtual**:

```bash
# En macOS/Linux:
source .venv/bin/activate

# En Windows:
.venv\Scripts\activate
```

4. **Instalar dependencias principales**:

```bash
pip install databento matplotlib python-dotenv
```

5. **Instalar dependencias adicionales para análisis avanzado**:

```bash
pip install pandas numpy python-dateutil
```

**📦 Resumen completo de dependencias:**

```bash
# Instalación completa en una línea
pip install databento matplotlib python-dotenv pandas numpy python-dateutil

# O usando requirements.txt (ver abajo)
pip install -r requirements.txt
```

**Crear archivo requirements.txt:**

```bash
# requirements.txt
databento>=0.64.0
matplotlib>=3.9.0
python-dotenv>=1.1.0
pandas>=2.3.0
numpy>=2.0.0
python-dateutil>=2.9.0
```

### 📚 **Descripción de Librerías**

| Librería          | Propósito                                | Usado en                                   |
| ----------------- | ---------------------------------------- | ------------------------------------------ |
| `databento`       | Cliente API para datos financieros       | Todos los scripts                          |
| `matplotlib`      | Generación de gráficos y visualizaciones | `plot_two_contract.py`, análisis avanzados |
| `python-dotenv`   | Manejo seguro de variables de entorno    | Todos los scripts (API keys)               |
| `pandas`          | Análisis y manipulación de datos         | `monthly_avg_diff.py`, proyecciones        |
| `numpy`           | Cálculos numéricos y estadísticos        | Análisis de tendencias, proyecciones       |
| `python-dateutil` | Manejo avanzado de fechas                | `monthly_projection_2026.py`               |

### 2. Variables de Entorno

Para proteger tu API key, este proyecto usa variables de entorno:

1. **Crea un archivo `.env`** en la raíz del proyecto:

```bash
# Databento API Configuration
DATABENTO_API_KEY=tu-api-key-aqui
```

2. **El archivo `.env` está protegido** por `.gitignore` y no se subirá a GitHub.

### 3. Obtener tu API Key

1. Regístrate en [Databento](https://databento.com)
2. Ve a tu dashboard y obtén tu API key
3. Reemplaza `tu-api-key-aqui` en el archivo `.env`

### 4. Ejecutar los Scripts

Con el entorno virtual activado, puedes ejecutar cualquier script:

```bash
# Asegúrate de que el entorno virtual esté activado
source .venv/bin/activate

# Ejecutar el script de plotting
python plot_two_contract.py

# Ejecutar análisis de volumen
python hight-volume-contracts.py

# Ejecutar análisis mensual
python monthly_avg_diff.py
```

### 5. Desactivar Entorno Virtual

Cuando termines de trabajar:

```bash
deactivate
```

---

## 📋 Tipos de Símbolos en Futuros

### Contratos Individuales (Formato Tradicional)

- **Formato**: `[ROOT][MES][AÑO]`
- **Ejemplo**: `ZCZ5` = Maíz, Diciembre 2025
- **Uso con Databento**: `stype_in="instrument_id"`
- **Característica**: Tiene fecha de vencimiento específica

### Contratos Continuos (Formato Databento)

- **Formato**: `[ROOT].[ROLL_RULE].[RANK]`
- **Ejemplo**: `ZC.c.0` = Maíz, calendar roll, front month
- **Uso con Databento**: `stype_in="continuous"`
- **Característica**: Se renueva automáticamente, sin vencimiento

### 📅 Códigos de Meses para Contratos Individuales

| Código  | Mes          | Español       | Ejemplo                          |
| ------- | ------------ | ------------- | -------------------------------- |
| `F`     | January      | Enero         | `ZCF5` = Maíz Enero 2025         |
| `G`     | February     | Febrero       | `ZCG5` = Maíz Febrero 2025       |
| `H`     | March        | Marzo         | `ZCH5` = Maíz Marzo 2025         |
| `J`     | April        | Abril         | `ZCJ5` = Maíz Abril 2025         |
| `K`     | May          | Mayo          | `ZCK5` = Maíz Mayo 2025          |
| `M`     | June         | Junio         | `ZCM5` = Maíz Junio 2025         |
| `N`     | July         | Julio         | `ZCN5` = Maíz Julio 2025         |
| `Q`     | August       | Agosto        | `ZCQ5` = Maíz Agosto 2025        |
| `U`     | September    | Septiembre    | `ZCU5` = Maíz Septiembre 2025    |
| `V`     | October      | Octubre       | `ZCV5` = Maíz Octubre 2025       |
| `X`     | November     | Noviembre     | `ZCX5` = Maíz Noviembre 2025     |
| **`Z`** | **December** | **Diciembre** | **`ZCZ5` = Maíz Diciembre 2025** |

### Ejemplos de Uso

```python
# ❌ Contrato individual (formato tradicional)
symbol = "ZCZ5"  # Maíz, Diciembre 2025 - SE VENCE el 14 de Diciembre 2025
stype_in = "instrument_id"

# ✅ Contrato continuo (formato Databento) - RECOMENDADO
symbol = "ZC.c.0"  # Maíz, calendar roll, front month - NUNCA SE VENCE
stype_in = "continuous"
```

---

## Formato de Símbolos para Contratos Continuos

En Databento, los símbolos para contratos continuos siguen el formato:

### `[ROOT].[ROLL_RULE].[RANK]`

---

## 1. **ROOT** (Raíz del instrumento)

Identifica el tipo de instrumento financiero:

- `ZC` = Corn (Maíz)
- `ZS` = Soybeans (Soja)
- `ZW` = Wheat (Trigo)
- `ES` = E-mini S&P 500
- `CL` = Crude Oil (Petróleo crudo)
- `GC` = Gold (Oro)

---

## 2. **ROLL_RULE** (Regla de rodaje/renovación)

Define cuándo y cómo se cambia de un contrato que vence al siguiente:

- `c` = **Calendar roll** (rodaje por calendario) - Común para commodities agrícolas
- `F` = **Front month** (mes frontal) - Cambia al contrato más activo
- `n` = **Next business day** (siguiente día hábil) - Común para índices
- `v` = **Volume roll** (rodaje por volumen) - Basado en el volumen de trading

---

## 3. **RANK** (Rango/posición del contrato)

Especifica qué contrato en la curva de futuros:

- `0` = Primer contrato (front month/más cercano al vencimiento)
- `1` = Segundo contrato
- `2` = Tercer contrato
- `3` = Cuarto contrato, etc.

---

## Ejemplos Prácticos

### Contratos Individuales vs Contratos Continuos

```python
# 📅 CONTRATOS INDIVIDUALES (Formato tradicional)
# Tienen fecha de vencimiento específica
data = client.timeseries.get_range(
    dataset="GLBX.MDP3",
    schema="ohlcv-1d",
    stype_in="instrument_id",  # ← Tipo para contratos individuales
    symbols=["ZCZ5", "ZSZ5", "ZWZ5"],  # Maíz, Soja, Trigo - Diciembre 2025
    start="2024-01-01",
    end="2025-12-14"  # ← Deben vencer antes de esta fecha
)

# 🔄 CONTRATOS CONTINUOS (Formato Databento) - RECOMENDADO
# Se renuevan automáticamente sin vencimiento
data = client.timeseries.get_range(
    dataset="GLBX.MDP3",
    schema="ohlcv-1d",
    stype_in="continuous",  # ← Tipo para contratos continuos
    symbols=["ZC.c.0", "ZS.c.0", "ZW.c.0"],  # Calendar roll, front month
    start="2024-01-01"  # ← Sin fecha de fin, van hasta hoy
)
```

### Más Ejemplos de Contratos Continuos

```python
# Commodities agrícolas con rodaje calendario
symbols = [
    "ZC.c.0",  # Maíz, rodaje calendario, primer contrato
    "ZS.c.0",  # Soja, rodaje calendario, primer contrato
    "ZW.c.0",  # Trigo, rodaje calendario, primer contrato
]

# Índices con rodaje por siguiente día hábil
symbols = [
    "ES.n.0",  # E-mini S&P 500, siguiente día hábil, primer contrato
    "ES.n.1",  # E-mini S&P 500, siguiente día hábil, segundo contrato
]

# Diferentes contratos del mismo commodity
symbols = [
    "ZC.F.0",  # Maíz, mes frontal, primer contrato
    "ZC.F.1",  # Maíz, mes frontal, segundo contrato
    "ZC.F.2",  # Maíz, mes frontal, tercer contrato
]
```

---

## ¿Por qué usar contratos continuos?

Los contratos de futuros individuales tienen fechas de vencimiento específicas. Los contratos continuos resuelven este problema:

1. **Concatenación automática**: Unen múltiples contratos individuales en una serie temporal continua
2. **Sin interrupciones**: Eliminan los vacíos cuando un contrato vence
3. **Análisis histórico**: Permiten análisis de largo plazo sin preocuparse por vencimientos
4. **Gestión de rollovers**: Manejan automáticamente la transición entre contratos

---

## Reglas de Rodaje más Comunes

### Calendar Roll (`c`)

- **Uso**: Commodities agrícolas (maíz, soja, trigo)
- **Lógica**: Sigue un calendario predefinido de cuándo cambiar contratos
- **Ventaja**: Predecible y consistente

### Next Business Day (`n`)

- **Uso**: Índices bursátiles (ES, NQ)
- **Lógica**: Cambia al siguiente día hábil antes del vencimiento
- **Ventaja**: Mantiene la liquidez máxima

### Front Month (`F`)

- **Uso**: Varios tipos de futuros
- **Lógica**: Siempre usa el contrato más activo/líquido
- **Ventaja**: Mayor volumen de trading

---

## Datasets Disponibles

- `GLBX.MDP3` - CME Globex (incluye futuros de commodities, índices, etc.)
- `XNAS.ITCH` - NASDAQ
- `XNYS.PILLAR` - NYSE
- Y muchos más...

Consulta la [documentación oficial de Databento](https://databento.com/docs) para la lista completa de datasets disponibles.

---

## 📁 Estructura del Proyecto

```
databento/
├── .env                                 # Variables de entorno (NO subir a Git)
├── .gitignore                          # Archivos a ignorar en Git
├── .venv/                              # Entorno virtual (NO subir a Git)
├── requirements.txt                    # Lista de dependencias del proyecto
├── README.md                           # Este archivo de documentación
│
├── 📊 Scripts Básicos:
├── plot_two_contract.py                # Script principal de plotting
├── hight-volume-contracts.py           # Análisis de volumen
├── monthly_avg_diff.py                 # Análisis de diferencias mensuales (original)
│
├── 🔍 Scripts de Exploración:
├── explore_2026_contract.py            # Explorar disponibilidad de contratos 2026
├── maiz_2026_analysis.py               # Análisis completo con gráficos 2026
│
├── 📈 Scripts de Análisis Avanzado:
├── monthly_futures_extended_2026.py    # Análisis mensual extendido (completo)
├── monthly_simple_2026.py              # Análisis mensual extendido (simple)
└── monthly_projection_2026.py          # Proyecciones mensuales hasta Oct 2026
```

### 🚀 Scripts por Funcionalidad

| **Script**                   | **Propósito**                  | **Resultado**                 |
| ---------------------------- | ------------------------------ | ----------------------------- |
| `plot_two_contract.py`       | Gráficos básicos de contratos  | Visualización simple          |
| `monthly_avg_diff.py`        | Análisis mensual original      | 3 meses de datos básicos      |
| `monthly_projection_2026.py` | **⭐ RECOMENDADO**             | Proyección hasta Oct 2026     |
| `maiz_2026_analysis.py`      | Análisis completo 2026         | Gráficos + análisis detallado |
| `explore_2026_contract.py`   | Explorar contratos disponibles | Diagnóstico de disponibilidad |

# Databento Futures Symbols Guide

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

4. **Instalar dependencias**:

```bash
pip install databento matplotlib python-dotenv
```

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
├── .env                     # Variables de entorno (NO subir a Git)
├── .gitignore              # Archivos a ignorar en Git
├── .venv/                  # Entorno virtual (NO subir a Git)
├── README.md               # Este archivo
├── plot_two_contract.py    # Script principal de plotting
├── hight-volume-contracts.py   # Análisis de volumen
└── monthly_avg_diff.py     # Análisis de diferencias mensuales
```

import databento as db
import pandas as pd
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener API key desde variable de entorno
api_key = os.getenv('DATABENTO_API_KEY')
if not api_key:
    raise ValueError("DATABENTO_API_KEY no encontrada en el archivo .env")

# Crear cliente histórico
client = db.Historical(api_key)

def monthly_avg_difference(symbol="ZCZ5", start="2025-01-15", end="2025-03-15"):
    # Obtener datos diarios
    data = client.timeseries.get_range(
        dataset="GLBX.MDP3",
        symbols=symbol,
        schema="ohlcv-1d",
        start=start,
        end=end,
    )

    # Convertir a DataFrame
    df = data.to_df().reset_index()  # ts_event pasa a columna
    df["month"] = df["ts_event"].dt.to_period("M")  # Ej: 2025-01
    # Agrupar por mes
    monthly = (
        df.groupby("month")
        .agg(
            open_avg=("open", "mean"),
            close_avg=("close", "mean")
        )
        .reset_index()
    )

    # Calcular diferencia (close - open)
    monthly["diff"] = monthly["close_avg"] - monthly["open_avg"]

    # Formato mes como MM/YY
    monthly["month"] = monthly["month"].dt.strftime("%m/%y")

    return monthly[["month", "open_avg", "close_avg", "diff"]]

# Ejecutar
monthly_data = monthly_avg_difference()
print(monthly_data)

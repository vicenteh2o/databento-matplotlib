import databento as db
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener API key desde variable de entorno
api_key = os.getenv('DATABENTO_API_KEY')
if not api_key:
    raise ValueError("DATABENTO_API_KEY no encontrada en el archivo .env")

client = db.Historical(api_key)

dataset = "GLBX.MDP3"
symbols = ["ZC.c.0", "ZS.c.0", "ZW.c.0"]  # Try with 'c' roll rule (calendar roll)
start = "2024"

data = client.timeseries.get_range(
    dataset="GLBX.MDP3",
    schema="ohlcv-1d",
    stype_in="continuous",
    symbols=symbols,
    start=start,
)

df = data.to_df()
df.groupby("symbol")["close"].plot(
    xlabel="Date",
    ylabel="Price",
)

plt.legend()
plt.show()

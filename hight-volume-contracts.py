import databento as db
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener API key desde variable de entorno
api_key = os.getenv('DATABENTO_API_KEY')
if not api_key:
    raise ValueError("DATABENTO_API_KEY no encontrada en el archivo .env")

# Create historical client
client = db.Historical(api_key)

def rank_by_volume(top=10):
    # Request OHLCV-1d data
    data = client.timeseries.get_range(
        dataset="GLBX.MDP3",
        symbols="ZCZ5",
        schema="ohlcv-1d",
        start="2025-01-15",
        end="2025-03-15",
        # encoding="json"
    )

    # Convert to DataFrame and filter for top 10 instruments by volume
    # df = data.to_df()
    # return df.sort_values(by="volume", ascending=False)["instrument_id"].to_list()[:top]
    return data.to_df()

top_instruments = rank_by_volume()
print(top_instruments)

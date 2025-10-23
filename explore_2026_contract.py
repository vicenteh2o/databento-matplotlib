import databento as db
import matplotlib.pyplot as plt
import pandas as pd
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener API key desde variable de entorno
api_key = os.getenv('DATABENTO_API_KEY')
if not api_key:
    raise ValueError("DATABENTO_API_KEY no encontrada en el archivo .env")

client = db.Historical(api_key)

print("🌽 Explorando contratos de maíz disponibles...")

# Función para probar un contrato individual
def test_individual_contract(symbol, year_desc):
    try:
        print(f"  Probando {symbol}...")
        data = client.timeseries.get_range(
            dataset="GLBX.MDP3",
            schema="ohlcv-1d",
            stype_in="instrument_id",
            symbols=[symbol],
            start="2024-01-01",
            end="2025-10-23"
        )
        
        df = data.to_df()
        if not df.empty:
            print(f"  ✅ {symbol}: {len(df)} registros encontrados")
            return df
        else:
            print(f"  ❌ {symbol}: Sin datos")
            return None
            
    except Exception as e:
        print(f"  ❌ {symbol}: Error - {str(e)}")
        return None

# 1. Probar contratos 2025 (que deberían existir)
print("\n📅 PASO 1: Probando contratos 2025 (disponibles):")
contracts_2025 = ["ZCH5", "ZCK5", "ZCN5", "ZCU5", "ZCZ5"]
available_2025 = []

for contract in contracts_2025:
    df = test_individual_contract(contract, "2025")
    if df is not None:
        available_2025.append((contract, df))

# 2. Probar contratos 2026 (puede que no existan aún)
print("\n📅 PASO 2: Probando contratos 2026 (experimental):")
contracts_2026 = ["ZCH6", "ZCK6", "ZCN6", "ZCU6", "ZCZ6"]
available_2026 = []

for contract in contracts_2026:
    df = test_individual_contract(contract, "2026")
    if df is not None:
        available_2026.append((contract, df))

# 3. Probar contratos continuos (curva de futuros)
print("\n🔄 PASO 3: Explorando contratos continuos (curva de futuros):")
continuous_symbols = ["ZC.c.0", "ZC.c.1", "ZC.c.2", "ZC.c.3", "ZC.c.4", "ZC.c.5"]

try:
    print(f"  Probando contratos continuos: {continuous_symbols}")
    data_continuous = client.timeseries.get_range(
        dataset="GLBX.MDP3",
        schema="ohlcv-1d",
        stype_in="continuous",
        symbols=continuous_symbols,
        start="2024-01-01",
        end="2025-10-23"
    )
    
    df_continuous = data_continuous.to_df()
    
    if not df_continuous.empty:
        print(f"  ✅ Contratos continuos: {len(df_continuous)} registros encontrados")
        print(f"  📊 Símbolos disponibles: {df_continuous['symbol'].unique().tolist()}")
        
        # Mostrar últimos precios
        print("\n  � Últimos precios por posición:")
        latest_prices = df_continuous.groupby('symbol')['close'].last()
        for symbol, price in latest_prices.items():
            print(f"    {symbol}: ${price:.2f}")
    else:
        print("  ❌ No se encontraron datos para contratos continuos")
        
except Exception as e:
    print(f"  ❌ Error con contratos continuos: {e}")

# 4. Visualizar resultados disponibles
print("\n� PASO 4: Generando gráficos de contratos disponibles...")

# Plotear contratos 2025 si están disponibles
if available_2025:
    plt.figure(figsize=(15, 8))
    
    # Subplot 1: Contratos individuales 2025
    plt.subplot(2, 2, 1)
    for contract, df in available_2025:
        plt.plot(df.index, df['close'], label=contract, linewidth=2)
    plt.title("Contratos Individuales Maíz 2025")
    plt.xlabel("Fecha")
    plt.ylabel("Precio")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Subplot 2: Contratos continuos si están disponibles
    if 'df_continuous' in locals() and not df_continuous.empty:
        plt.subplot(2, 2, 2)
        for symbol in df_continuous['symbol'].unique():
            symbol_data = df_continuous[df_continuous['symbol'] == symbol]
            plt.plot(symbol_data.index, symbol_data['close'], label=symbol, linewidth=2)
        plt.title("Curva de Futuros Maíz (Contratos Continuos)")
        plt.xlabel("Fecha")  
        plt.ylabel("Precio")
        plt.legend()
        plt.grid(True, alpha=0.3)
    
    # Subplot 3: Comparación si hay contratos 2026
    if available_2026:
        plt.subplot(2, 2, 3)
        for contract, df in available_2026:
            plt.plot(df.index, df['close'], label=contract, linewidth=2)
        plt.title("Contratos Individuales Maíz 2026")
        plt.xlabel("Fecha")
        plt.ylabel("Precio")
        plt.legend()
        plt.grid(True, alpha=0.3)
    
    # Subplot 4: Resumen de precios actuales
    plt.subplot(2, 2, 4)
    current_prices = []
    labels = []
    
    for contract, df in available_2025:
        current_prices.append(df['close'].iloc[-1])
        labels.append(contract)
    
    if available_2026:
        for contract, df in available_2026:
            current_prices.append(df['close'].iloc[-1])
            labels.append(contract)
    
    plt.bar(labels, current_prices, color=['green']*len(available_2025) + ['blue']*len(available_2026))
    plt.title("Precios Actuales por Contrato")
    plt.xlabel("Contrato")
    plt.ylabel("Precio")
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

else:
    print("  ❌ No hay datos disponibles para generar gráficos")

# 5. Resumen final
print("\n📝 RESUMEN FINAL:")
print(f"  • Contratos 2025 disponibles: {len(available_2025)}")
print(f"  • Contratos 2026 disponibles: {len(available_2026)}")

if available_2025:
    print(f"  • Contratos 2025 encontrados: {[c[0] for c in available_2025]}")

if available_2026:
    print(f"  • Contratos 2026 encontrados: {[c[0] for c in available_2026]}")
    print("  ✅ ¡Excelente! Los contratos 2026 ya están disponibles")
else:
    print("  ❌ Los contratos 2026 aún no están disponibles en Databento")
    print("  💡 Recomendación: Usa contratos continuos (ZC.c.X) para proyecciones")

print("\n🎯 PRÓXIMOS PASOS:")
print("  1. Para análisis actual: Usa contratos 2025 disponibles")
print("  2. Para proyecciones: Usa contratos continuos (ZC.c.0, ZC.c.1, etc.)")
print("  3. Revisa periódicamente la disponibilidad de contratos 2026")
print("  4. Los contratos futuros suelen listarse 18-24 meses antes del vencimiento")
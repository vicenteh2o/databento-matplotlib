import databento as db
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener API key desde variable de entorno
api_key = os.getenv('DATABENTO_API_KEY')
if not api_key:
    raise ValueError("DATABENTO_API_KEY no encontrada en el archivo .env")

client = db.Historical(api_key)

print("🌽 Analizando proyecciones de maíz hacia 2026 usando contratos continuos...")

# Usar contratos continuos que se extienden hacia 2026
symbols_2026_projection = [
    "ZC.c.0",  # Front month (actual)
    "ZC.c.1",  # 2do mes
    "ZC.c.2",  # 3er mes  
    "ZC.c.3",  # 4to mes (probablemente 2026)
    "ZC.c.4",  # 5to mes (definitivamente 2026)
    "ZC.c.5",  # 6to mes (2026)
]

print(f"📊 Obteniendo datos para: {symbols_2026_projection}")

try:
    data = client.timeseries.get_range(
        dataset="GLBX.MDP3",
        schema="ohlcv-1d",
        stype_in="continuous",
        symbols=symbols_2026_projection,
        start="2024-01-01",
        end="2025-10-23"
    )
    
    df = data.to_df()
    
    if not df.empty:
        print(f"✅ Datos obtenidos: {len(df)} registros")
        
        # Análisis de precios actuales
        print("\n📈 PRECIOS ACTUALES (Oct 2025):")
        latest_prices = df.groupby('symbol')['close'].last()
        for symbol, price in latest_prices.items():
            if symbol in ['ZC.c.3', 'ZC.c.4', 'ZC.c.5']:
                print(f"  {symbol}: ${price:.2f} ⭐ (Proyección 2026)")
            else:
                print(f"  {symbol}: ${price:.2f}")
        
        # Crear visualización completa
        plt.figure(figsize=(16, 10))
        
        # Gráfico 1: Evolución temporal de todos los contratos
        plt.subplot(2, 3, 1)
        colors = ['red', 'orange', 'yellow', 'lightgreen', 'green', 'darkgreen']
        for i, symbol in enumerate(df['symbol'].unique()):
            symbol_data = df[df['symbol'] == symbol]
            plt.plot(symbol_data.index, symbol_data['close'], 
                    label=symbol, linewidth=2, color=colors[i % len(colors)])
        plt.title("Evolución de Precios - Curva de Futuros")
        plt.xlabel("Fecha")
        plt.ylabel("Precio ($)")
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Gráfico 2: Curva de futuros actual (contango/backwardation)
        plt.subplot(2, 3, 2)
        contracts = latest_prices.index.tolist()
        prices = latest_prices.values.tolist()
        
        colors_bar = ['red' if 'c.0' in c or 'c.1' in c or 'c.2' in c 
                     else 'green' for c in contracts]
        
        bars = plt.bar(range(len(contracts)), prices, color=colors_bar, alpha=0.7)
        plt.title("Curva de Futuros Actual\n(Verde = Proyección 2026)")
        plt.xlabel("Contrato")
        plt.ylabel("Precio ($)")
        plt.xticks(range(len(contracts)), contracts, rotation=45)
        
        # Añadir valores en las barras
        for i, (bar, price) in enumerate(zip(bars, prices)):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                    f'${price:.0f}', ha='center', va='bottom', fontweight='bold')
        plt.grid(True, alpha=0.3)
        
        # Gráfico 3: Spread entre contratos (contango analysis)
        plt.subplot(2, 3, 3)
        spreads = []
        spread_labels = []
        
        contracts_sorted = sorted(latest_prices.index)
        for i in range(1, len(contracts_sorted)):
            spread = latest_prices[contracts_sorted[i]] - latest_prices[contracts_sorted[i-1]]
            spreads.append(spread)
            spread_labels.append(f"{contracts_sorted[i-1]}\nvs\n{contracts_sorted[i]}")
        
        colors_spread = ['red' if s > 0 else 'blue' for s in spreads]
        bars_spread = plt.bar(range(len(spreads)), spreads, color=colors_spread, alpha=0.7)
        plt.title("Spreads entre Contratos\n(Rojo=Contango, Azul=Backwardation)")
        plt.xlabel("Par de Contratos")
        plt.ylabel("Diferencia de Precio ($)")
        plt.xticks(range(len(spread_labels)), spread_labels, rotation=45)
        plt.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        plt.grid(True, alpha=0.3)
        
        # Gráfico 4: Análisis de volatilidad
        plt.subplot(2, 3, 4)
        volatilities = df.groupby('symbol')['close'].std()
        bars_vol = plt.bar(volatilities.index, volatilities.values, 
                          color='purple', alpha=0.7)
        plt.title("Volatilidad por Contrato")
        plt.xlabel("Contrato")
        plt.ylabel("Volatilidad ($)")
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        
        # Gráfico 5: Retornos diarios promedio
        plt.subplot(2, 3, 5)
        returns = df.groupby('symbol')['close'].pct_change().groupby(df['symbol']).mean() * 100
        colors_ret = ['red' if r < 0 else 'green' for r in returns.values]
        bars_ret = plt.bar(returns.index, returns.values, color=colors_ret, alpha=0.7)
        plt.title("Retorno Diario Promedio (%)")
        plt.xlabel("Contrato")
        plt.ylabel("Retorno Diario (%)")
        plt.xticks(rotation=45)
        plt.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        plt.grid(True, alpha=0.3)
        
        # Gráfico 6: Proyección simple de tendencia
        plt.subplot(2, 3, 6)
        
        # Calcular tendencias para contratos 2026
        projection_contracts = ['ZC.c.3', 'ZC.c.4', 'ZC.c.5']
        
        for contract in projection_contracts:
            if contract in df['symbol'].unique():
                contract_data = df[df['symbol'] == contract]['close']
                
                # Calcular tendencia lineal simple (últimos 30 días)
                recent_data = contract_data.tail(30)
                if len(recent_data) > 1:
                    x = range(len(recent_data))
                    z = np.polyfit(x, recent_data.values, 1)
                    trend_line = np.poly1d(z)
                    
                    # Proyectar 30 días más
                    future_x = range(len(recent_data), len(recent_data) + 30)
                    future_prices = trend_line(future_x)
                    
                    plt.plot(x, recent_data.values, 'o-', label=f'{contract} (Actual)', linewidth=2)
                    plt.plot(future_x, future_prices, '--', label=f'{contract} (Proyección)', linewidth=2)
        
        plt.title("Proyección de Tendencia (30 días)\nContratos 2026")
        plt.xlabel("Días")
        plt.ylabel("Precio ($)")
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        # Resumen de análisis
        print("\n📊 ANÁLISIS DE PROYECCIONES 2026:")
        print("="*50)
        
        # Identificar si hay contango o backwardation
        front_price = latest_prices['ZC.c.0']
        far_price = latest_prices['ZC.c.5']
        
        if far_price > front_price:
            market_structure = "CONTANGO"
            print(f"🔴 Mercado en {market_structure}: Los precios futuros son más altos")
            print(f"   Front month: ${front_price:.2f}")
            print(f"   6to mes (2026): ${far_price:.2f}")
            print(f"   Diferencia: +${far_price - front_price:.2f}")
        else:
            market_structure = "BACKWARDATION"
            print(f"🔵 Mercado en {market_structure}: Los precios futuros son más bajos")
            print(f"   Front month: ${front_price:.2f}")
            print(f"   6to mes (2026): ${far_price:.2f}")
            print(f"   Diferencia: ${far_price - front_price:.2f}")
        
        print(f"\n🎯 CONTRATOS PARA EXPOSICIÓN 2026:")
        for contract in ['ZC.c.3', 'ZC.c.4', 'ZC.c.5']:
            if contract in latest_prices:
                price = latest_prices[contract]
                print(f"   {contract}: ${price:.2f}")
        
        print(f"\n💡 INTERPRETACIÓN:")
        print(f"   • Los contratos ZC.c.3, ZC.c.4, ZC.c.5 te dan exposición a precios de 2026")
        print(f"   • El mercado está en {market_structure}")
        if market_structure == "CONTANGO":
            print(f"   • Esto sugiere expectativa de precios más altos en el futuro")
            print(f"   • Posible escasez esperada o costos de almacenamiento")
        else:
            print(f"   • Esto sugiere expectativa de precios más bajos en el futuro")
            print(f"   • Posible abundancia esperada o presión de inventarios")
            
    else:
        print("❌ No se encontraron datos")
        
except Exception as e:
    print(f"❌ Error: {e}")

print(f"\n🚀 CONCLUSIÓN:")
print(f"✅ SÍ puedes ver contratos futuros para 2026 usando:")
print(f"   • ZC.c.3, ZC.c.4, ZC.c.5 (contratos continuos)")
print(f"   • Estos te dan exposición a precios que se extienden hacia 2026")
print(f"   • Mucho mejor que esperar a que listen contratos individuales ZCH6, etc.")

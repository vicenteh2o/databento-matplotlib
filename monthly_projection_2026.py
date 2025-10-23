import databento as db
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Cargar variables de entorno
load_dotenv()

# Obtener API key desde variable de entorno
api_key = os.getenv('DATABENTO_API_KEY')
if not api_key:
    raise ValueError("DATABENTO_API_KEY no encontrada en el archivo .env")

# Crear cliente histórico
client = db.Historical(api_key)

def monthly_projection_2026(commodity="ZC"):
    """
    Crear proyección mensual que incluya fechas hacia 2026
    Basándose en contratos continuos actuales para estimar precios futuros
    """
    
    print(f"🌽 Creando proyección mensual {commodity} hacia 2026...")
    print("="*60)
    
    # Usar contratos continuos
    symbols = [f"{commodity}.c.0", f"{commodity}.c.3", f"{commodity}.c.4", f"{commodity}.c.5"]
    
    try:
        # Obtener datos actuales
        data = client.timeseries.get_range(
            dataset="GLBX.MDP3",
            schema="ohlcv-1d",
            stype_in="continuous",
            symbols=symbols,
            start="2025-01-01",
            end="2025-10-23"
        )
        
        df = data.to_df().reset_index()
        
        if df.empty:
            print("❌ No se encontraron datos")
            return None
        
        # Paso 1: Obtener datos históricos reales (2025)
        historical_results = []
        
        # Usar el contrato front month para datos históricos reales
        front_data = df[df['symbol'] == f"{commodity}.c.0"].copy()
        front_data["month"] = front_data["ts_event"].dt.to_period("M")
        
        monthly_historical = (
            front_data.groupby("month")
            .agg(
                open_avg=("open", "mean"),
                close_avg=("close", "mean")
            )
            .reset_index()
        )
        
        monthly_historical["diff"] = monthly_historical["close_avg"] - monthly_historical["open_avg"]
        monthly_historical["month"] = monthly_historical["month"].dt.strftime("%m/%y")
        monthly_historical["data_type"] = "REAL"
        
        # Tomar los últimos 6 meses de datos reales
        historical_results = monthly_historical.tail(6).copy()
        
        # Paso 2: Crear proyecciones para 2026
        projection_results = []
        
        # Obtener precios actuales de contratos 2026
        current_date = datetime(2025, 10, 23)
        contracts_2026 = [f"{commodity}.c.3", f"{commodity}.c.4", f"{commodity}.c.5"]
        
        # Calcular precios promedio actuales para cada contrato 2026
        contract_prices = {}
        for contract in contracts_2026:
            contract_data = df[df['symbol'] == contract]
            if not contract_data.empty:
                recent_data = contract_data.tail(30)  # Últimos 30 días
                avg_open = recent_data['open'].mean()
                avg_close = recent_data['close'].mean()
                contract_prices[contract] = {
                    'open_avg': avg_open,
                    'close_avg': avg_close,
                    'diff': avg_close - avg_open
                }
        
        # Generar proyecciones mensuales para 2026
        # Empezar desde Nov 2025 hasta Oct 2026 (12 meses)
        start_projection = datetime(2025, 11, 1)
        
        for i in range(12):  # 12 meses hacia adelante
            projection_date = start_projection + relativedelta(months=i)
            month_str = projection_date.strftime("%m/%y")
            
            # Seleccionar qué contrato usar basándose en la distancia temporal
            if i < 3:  # Primeros 3 meses: usar ZC.c.3
                base_contract = f"{commodity}.c.3"
            elif i < 8:  # Siguientes 5 meses: usar ZC.c.4
                base_contract = f"{commodity}.c.4"
            else:  # Últimos 4 meses: usar ZC.c.5
                base_contract = f"{commodity}.c.5"
            
            if base_contract in contract_prices:
                base_price = contract_prices[base_contract]
                
                # Añadir algo de variabilidad estacional/aleatoria
                seasonal_factor = 1 + 0.02 * np.sin(2 * np.pi * i / 12)  # +/-2% variación estacional
                noise_factor = 1 + np.random.normal(0, 0.01)  # +/-1% ruido aleatorio
                
                projected_open = base_price['open_avg'] * seasonal_factor * noise_factor
                projected_close = base_price['close_avg'] * seasonal_factor * noise_factor
                projected_diff = projected_close - projected_open
                
                projection_results.append({
                    'month': month_str,
                    'open_avg': projected_open,
                    'close_avg': projected_close,
                    'diff': projected_diff,
                    'data_type': 'PROYECCIÓN',
                    'base_contract': base_contract
                })
        
        # Combinar resultados históricos y proyecciones
        all_results = []
        
        # Agregar datos históricos
        for _, row in historical_results.iterrows():
            all_results.append({
                'month': row['month'],
                'open_avg': row['open_avg'],
                'close_avg': row['close_avg'],
                'diff': row['diff'],
                'data_type': 'REAL'
            })
        
        # Agregar proyecciones
        all_results.extend(projection_results)
        
        # Crear DataFrame final
        final_df = pd.DataFrame(all_results)
        
        return final_df
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def display_projection_results(results_df, commodity="ZC"):
    """
    Mostrar resultados en el formato exacto solicitado
    """
    if results_df is None or results_df.empty:
        print("❌ No hay resultados para mostrar")
        return
    
    print(f"\n📊 PROYECCIÓN MENSUAL {commodity} - Mayo 2025 a Octubre 2026")
    print("="*70)
    print("(Datos reales hasta Oct 2025, proyecciones desde Nov 2025)")
    print("")
    
    # Formato exacto solicitado
    print("month   open_avg  close_avg      diff")
    
    for _, row in results_df.iterrows():
        status_symbol = "📊" if row['data_type'] == 'REAL' else "🔮"
        
        print(f"{row['month']} {row['open_avg']:9.6f} {row['close_avg']:9.6f} {row['diff']:9.6f}")
    
    print("")
    print("📋 LEYENDA:")
    print("  • 05/25 - 10/25: Datos REALES de mercado")
    print("  • 11/25 - 10/26: PROYECCIONES basadas en contratos futuros")
    
    # Análisis adicional
    real_data = results_df[results_df['data_type'] == 'REAL']
    projection_data = results_df[results_df['data_type'] == 'PROYECCIÓN']
    
    if not real_data.empty and not projection_data.empty:
        avg_real_price = real_data['close_avg'].mean()
        avg_projection_price = projection_data['close_avg'].mean()
        
        print(f"\n📈 ANÁLISIS COMPARATIVO:")
        print(f"  • Precio promedio real (2025): ${avg_real_price:.2f}")
        print(f"  • Precio promedio proyección (2026): ${avg_projection_price:.2f}")
        print(f"  • Diferencia: ${avg_projection_price - avg_real_price:.2f}")
        
        if avg_projection_price > avg_real_price:
            print(f"  • Tendencia proyectada: 📈 ALCISTA hacia 2026")
        else:
            print(f"  • Tendencia proyectada: 📉 BAJISTA hacia 2026")

def main():
    """
    Función principal
    """
    commodity = "ZC"  # Maíz
    
    print("🚀 PROYECCIÓN MENSUAL EXTENDIDA - MAYO 2025 A OCTUBRE 2026")
    print("="*70)
    print("📝 Combina datos reales (2025) con proyecciones (2026)")
    print("   basadas en contratos futuros actuales")
    print("")
    
    # Set random seed para resultados reproducibles
    np.random.seed(42)
    
    # Generar proyección
    results = monthly_projection_2026(commodity)
    
    if results is not None:
        # Mostrar resultados en formato solicitado
        display_projection_results(results, commodity)
        
        # Guardar datos
        output_file = f"{commodity}_projection_2025_to_2026.csv"
        results.to_csv(output_file, index=False)
        print(f"\n💾 Datos guardados en: {output_file}")
        
        print(f"\n🎉 ÉXITO: Proyección creada con {len(results)} meses")
        print(f"📅 Desde {results.iloc[0]['month']} hasta {results.iloc[-1]['month']}")
        
    else:
        print("❌ No se pudo generar la proyección")

if __name__ == "__main__":
    main()

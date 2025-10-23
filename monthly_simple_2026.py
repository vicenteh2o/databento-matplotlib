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

def monthly_futures_simple(commodity="ZC", extended_to_2026=True):
    """
    Versión simplificada del análisis mensual con proyecciones 2026
    Similar al monthly_avg_diff.py original pero con contratos futuros extendidos
    """
    
    print(f"🌽 Análisis mensual {commodity} - Extendido hacia 2026")
    print("="*60)
    
    # Usar contratos continuos que se extienden hacia 2026
    if extended_to_2026:
        symbols = [
            f"{commodity}.c.0",  # Actual
            f"{commodity}.c.1",  # 2do mes  
            f"{commodity}.c.2",  # 3er mes
            f"{commodity}.c.3",  # 4to mes (2026)
            f"{commodity}.c.4",  # 5to mes (2026)
            f"{commodity}.c.5",  # 6to mes (2026)
        ]
    else:
        symbols = [f"{commodity}.c.0"]  # Solo front month
    
    try:
        # Obtener datos
        data = client.timeseries.get_range(
            dataset="GLBX.MDP3",
            schema="ohlcv-1d",
            stype_in="continuous",
            symbols=symbols,
            start="2024-01-01",
            end="2025-10-23"
        )
        
        df = data.to_df().reset_index()
        
        if df.empty:
            print("❌ No se encontraron datos")
            return None
        
        # Procesar cada contrato por separado
        all_results = []
        
        for symbol in symbols:
            symbol_data = df[df['symbol'] == symbol].copy()
            
            if symbol_data.empty:
                continue
            
            # Agregar columna de mes
            symbol_data["month"] = symbol_data["ts_event"].dt.to_period("M")
            
            # Agrupar por mes (similar al original)
            monthly = (
                symbol_data.groupby("month")
                .agg(
                    open_avg=("open", "mean"),
                    close_avg=("close", "mean")
                )
                .reset_index()
            )
            
            # Calcular diferencia (close - open) - igual que el original
            monthly["diff"] = monthly["close_avg"] - monthly["open_avg"]
            
            # Formato mes como MM/YY - igual que el original
            monthly["month"] = monthly["month"].dt.strftime("%m/%y")
            
            # Agregar información del contrato
            monthly["contract"] = symbol
            monthly["is_2026_projection"] = symbol.endswith(('.c.3', '.c.4', '.c.5'))
            
            # Tomar solo los últimos meses para no sobrecargar
            recent_monthly = monthly.tail(6)  # Últimos 6 meses
            
            all_results.append(recent_monthly)
        
        # Combinar resultados
        if all_results:
            combined_df = pd.concat(all_results, ignore_index=True)
            return combined_df
        else:
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def display_results(results_df, commodity="ZC"):
    """
    Mostrar resultados en formato similar al monthly_avg_diff.py original
    """
    if results_df is None or results_df.empty:
        print("❌ No hay resultados para mostrar")
        return
    
    print(f"\n📊 RESULTADOS FORMATO ORIGINAL - {commodity}")
    print("="*70)
    
    # Mostrar por contrato
    for contract in results_df['contract'].unique():
        contract_data = results_df[results_df['contract'] == contract]
        
        is_2026 = contract_data['is_2026_projection'].iloc[0]
        status = "⭐ PROYECCIÓN 2026" if is_2026 else "📊 ACTUAL/2025"
        
        print(f"\n🔹 {contract} - {status}")
        print("-" * 50)
        
        # Formato igual al original
        display_df = contract_data[['month', 'open_avg', 'close_avg', 'diff']].copy()
        
        # Formatear números como en el original
        display_df['open_avg'] = display_df['open_avg'].round(6)
        display_df['close_avg'] = display_df['close_avg'].round(6) 
        display_df['diff'] = display_df['diff'].round(6)
        
        print(display_df.to_string(index=False))
    
    print(f"\n📋 RESUMEN CONSOLIDADO - Todos los contratos:")
    print("="*70)
    print(f"{'Contrato':<10} {'Mes':<8} {'Open Avg':<12} {'Close Avg':<12} {'Diff':<10} {'2026?'}")
    print("-" * 70)
    
    # Tomar el último mes de cada contrato para el resumen
    summary_data = []
    for contract in results_df['contract'].unique():
        contract_data = results_df[results_df['contract'] == contract]
        latest = contract_data.iloc[-1]
        
        status = "⭐ SÍ" if latest['is_2026_projection'] else "❌ No"
        
        print(f"{contract:<10} {latest['month']:<8} "
              f"{latest['open_avg']:<12.2f} {latest['close_avg']:<12.2f} "
              f"{latest['diff']:<10.2f} {status}")
        
        summary_data.append({
            'contract': contract,
            'month': latest['month'],
            'open_avg': latest['open_avg'],
            'close_avg': latest['close_avg'],
            'diff': latest['diff'],
            'is_2026': latest['is_2026_projection']
        })
    
    # Análisis adicional
    summary_df = pd.DataFrame(summary_data)
    
    print(f"\n🎯 ANÁLISIS COMPARATIVO:")
    print("="*50)
    
    # Contratos 2026
    contratos_2026 = summary_df[summary_df['is_2026'] == True]
    if not contratos_2026.empty:
        print(f"✅ Contratos con exposición 2026: {len(contratos_2026)}")
        
        avg_price_2026 = contratos_2026['close_avg'].mean()
        avg_diff_2026 = contratos_2026['diff'].mean()
        
        print(f"   • Precio promedio 2026: ${avg_price_2026:.2f}")
        print(f"   • Diferencia promedio 2026: ${avg_diff_2026:.2f}")
        
        if avg_diff_2026 > 0:
            print(f"   • Tendencia 2026: 📈 ALCISTA")
        else:
            print(f"   • Tendencia 2026: 📉 BAJISTA")
    
    # Contratos actuales
    contratos_actuales = summary_df[summary_df['is_2026'] == False]
    if not contratos_actuales.empty:
        avg_price_actual = contratos_actuales['close_avg'].mean()
        avg_diff_actual = contratos_actuales['diff'].mean()
        
        print(f"✅ Contratos actuales/2025: {len(contratos_actuales)}")
        print(f"   • Precio promedio actual: ${avg_price_actual:.2f}")
        print(f"   • Diferencia promedio actual: ${avg_diff_actual:.2f}")
        
        # Comparación
        if len(contratos_2026) > 0:
            premium_2026 = avg_price_2026 - avg_price_actual
            print(f"\n💰 PREMIUM 2026 vs ACTUAL: ${premium_2026:.2f}")
            
            if premium_2026 > 0:
                print(f"   🔴 Mercado en CONTANGO (futuros más caros)")
            else:
                print(f"   🔵 Mercado en BACKWARDATION (futuros más baratos)")

def main():
    """
    Función principal - Ejecutar análisis
    """
    commodity = "ZC"  # Maíz - puedes cambiar por ZS (soja) o ZW (trigo)
    
    print("🚀 MONTHLY_AVG_DIFF EXTENDIDO - PROYECCIONES 2026")
    print("="*60)
    print("📝 Basado en monthly_avg_diff.py original pero extendido")
    print("   con contratos futuros que llegan hasta 2026")
    print("")
    
    # Ejecutar análisis
    results = monthly_futures_simple(commodity, extended_to_2026=True)
    
    if results is not None:
        # Mostrar resultados
        display_results(results, commodity)
        
        # Guardar en CSV para referencia
        output_file = f"{commodity}_monthly_extended_simple.csv"
        results.to_csv(output_file, index=False)
        print(f"\n💾 Datos guardados en: {output_file}")
        
        print(f"\n🎉 ÉXITO: Análisis completado con {len(results)} registros mensuales")
        print(f"📈 Ahora tienes proyecciones hasta 2026 vs solo 3 meses del original")
        
    else:
        print("❌ No se pudieron obtener resultados")

if __name__ == "__main__":
    main()

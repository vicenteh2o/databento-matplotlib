import databento as db
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Cargar variables de entorno
load_dotenv()

# Obtener API key desde variable de entorno
api_key = os.getenv('DATABENTO_API_KEY')
if not api_key:
    raise ValueError("DATABENTO_API_KEY no encontrada en el archivo .env")

# Crear cliente histórico
client = db.Historical(api_key)

def monthly_futures_analysis(commodity="ZC", start_date="2024-01-01", end_date="2025-10-23"):
    """
    Análisis mensual extendido para contratos futuros usando contratos continuos
    que se extienden hacia 2026
    
    Args:
        commodity: Root symbol (ZC, ZS, ZW, etc.)
        start_date: Fecha inicio
        end_date: Fecha fin
    
    Returns:
        DataFrame con análisis mensual extendido
    """
    
    print(f"🌽 Analizando {commodity} - Proyecciones mensuales hacia 2026...")
    
    # Usar contratos continuos que se extienden hacia 2026
    symbols = [
        f"{commodity}.c.0",  # Front month (actual)
        f"{commodity}.c.1",  # 2do mes
        f"{commodity}.c.2",  # 3er mes
        f"{commodity}.c.3",  # 4to mes (llega a 2026)
        f"{commodity}.c.4",  # 5to mes (definitivamente 2026)
        f"{commodity}.c.5",  # 6to mes (2026)
    ]
    
    print(f"📊 Obteniendo datos para: {symbols}")
    
    try:
        # Obtener datos históricos
        data = client.timeseries.get_range(
            dataset="GLBX.MDP3",
            schema="ohlcv-1d",
            stype_in="continuous",  # ← Clave: usar contratos continuos
            symbols=symbols,
            start=start_date,
            end=end_date
        )
        
        df = data.to_df().reset_index()
        
        if df.empty:
            print("❌ No se encontraron datos")
            return None
            
        print(f"✅ Datos obtenidos: {len(df)} registros")
        
        # Agregar columna de mes-año
        df["month_year"] = df["ts_event"].dt.to_period("M")
        
        # Análisis mensual por contrato
        monthly_analysis = []
        
        for symbol in symbols:
            symbol_data = df[df['symbol'] == symbol].copy()
            
            if symbol_data.empty:
                continue
                
            # Agrupar por mes
            monthly_symbol = (
                symbol_data.groupby("month_year")
                .agg(
                    open_avg=("open", "mean"),
                    close_avg=("close", "mean"),
                    high_avg=("high", "mean"),
                    low_avg=("low", "mean"),
                    volume_avg=("volume", "mean"),
                    days_count=("open", "count")
                )
                .reset_index()
            )
            
            # Calcular métricas adicionales
            monthly_symbol["diff"] = monthly_symbol["close_avg"] - monthly_symbol["open_avg"]
            monthly_symbol["range_avg"] = monthly_symbol["high_avg"] - monthly_symbol["low_avg"] 
            monthly_symbol["symbol"] = symbol
            monthly_symbol["month"] = monthly_symbol["month_year"].dt.strftime("%m/%y")
            
            # Determinar si es proyección 2026
            monthly_symbol["is_2026_projection"] = symbol in [f"{commodity}.c.3", f"{commodity}.c.4", f"{commodity}.c.5"]
            
            monthly_analysis.append(monthly_symbol)
        
        # Concatenar todos los resultados
        if not monthly_analysis:
            print("❌ No se pudo procesar ningún símbolo")
            return None
            
        all_monthly = pd.concat(monthly_analysis, ignore_index=True)
        
        # Ordenar por símbolo y mes
        all_monthly = all_monthly.sort_values(['symbol', 'month_year'])
        
        return all_monthly
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def create_extended_summary(monthly_df, commodity="ZC"):
    """
    Crear resumen extendido similar al original pero con proyecciones 2026
    """
    if monthly_df is None or monthly_df.empty:
        return None
    
    print(f"\n📊 RESUMEN MENSUAL EXTENDIDO - {commodity} (Incluye proyecciones 2026)")
    print("="*80)
    
    # Resumen por contrato
    summary_by_contract = []
    
    for symbol in monthly_df['symbol'].unique():
        symbol_data = monthly_df[monthly_df['symbol'] == symbol]
        
        print(f"\n🔹 {symbol}:")
        if symbol_data['is_2026_projection'].iloc[0]:
            print("   ⭐ PROYECCIÓN 2026")
        
        # Mostrar últimos 6 meses de datos
        recent_data = symbol_data.tail(6)
        
        for _, row in recent_data.iterrows():
            status = "📈 2026" if row['is_2026_projection'] else "📊 2025"
            print(f"   {status} {row['month']:>5} | Open: ${row['open_avg']:>7.2f} | Close: ${row['close_avg']:>7.2f} | Diff: ${row['diff']:>6.2f}")
        
        # Agregar al resumen
        latest = symbol_data.iloc[-1]
        summary_by_contract.append({
            'contract': symbol,
            'latest_month': latest['month'],
            'open_avg': latest['open_avg'],
            'close_avg': latest['close_avg'],
            'diff': latest['diff'],
            'is_2026': latest['is_2026_projection']
        })
    
    # Crear DataFrame de resumen
    summary_df = pd.DataFrame(summary_by_contract)
    
    return summary_df

def visualize_extended_analysis(monthly_df, commodity="ZC"):
    """
    Crear visualizaciones del análisis extendido
    """
    if monthly_df is None or monthly_df.empty:
        return
    
    plt.figure(figsize=(20, 12))
    
    # Colores para cada contrato
    colors = {
        f'{commodity}.c.0': 'red',
        f'{commodity}.c.1': 'orange', 
        f'{commodity}.c.2': 'gold',
        f'{commodity}.c.3': 'lightgreen',
        f'{commodity}.c.4': 'green',
        f'{commodity}.c.5': 'darkgreen'
    }
    
    # Gráfico 1: Evolución mensual de precios promedio
    plt.subplot(2, 3, 1)
    for symbol in monthly_df['symbol'].unique():
        symbol_data = monthly_df[monthly_df['symbol'] == symbol]
        
        label = f"{symbol} {'(2026 Proj.)' if symbol.endswith(('.c.3', '.c.4', '.c.5')) else ''}"
        
        plt.plot(symbol_data['month_year'].astype(str), 
                symbol_data['close_avg'], 
                'o-', label=label, 
                color=colors.get(symbol, 'blue'),
                linewidth=2, markersize=4)
    
    plt.title(f'{commodity} - Evolución Mensual de Precios Promedio')
    plt.xlabel('Mes/Año')
    plt.ylabel('Precio Promedio ($)')
    plt.xticks(rotation=45)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    
    # Gráfico 2: Diferencias mensuales (close - open)
    plt.subplot(2, 3, 2)
    for symbol in monthly_df['symbol'].unique():
        symbol_data = monthly_df[monthly_df['symbol'] == symbol]
        
        label = f"{symbol} {'(2026 Proj.)' if symbol.endswith(('.c.3', '.c.4', '.c.5')) else ''}"
        
        plt.plot(symbol_data['month_year'].astype(str), 
                symbol_data['diff'], 
                'o-', label=label,
                color=colors.get(symbol, 'blue'),
                linewidth=2, markersize=4)
    
    plt.title(f'{commodity} - Diferencias Mensuales (Close - Open)')
    plt.xlabel('Mes/Año')
    plt.ylabel('Diferencia ($)')
    plt.xticks(rotation=45)
    plt.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    
    # Gráfico 3: Rango promedio mensual (volatilidad)
    plt.subplot(2, 3, 3)
    for symbol in monthly_df['symbol'].unique():
        symbol_data = monthly_df[monthly_df['symbol'] == symbol]
        
        label = f"{symbol} {'(2026 Proj.)' if symbol.endswith(('.c.3', '.c.4', '.c.5')) else ''}"
        
        plt.plot(symbol_data['month_year'].astype(str), 
                symbol_data['range_avg'], 
                'o-', label=label,
                color=colors.get(symbol, 'blue'),
                linewidth=2, markersize=4)
    
    plt.title(f'{commodity} - Rango Promedio Mensual (Volatilidad)')
    plt.xlabel('Mes/Año')
    plt.ylabel('Rango Promedio ($)')
    plt.xticks(rotation=45)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    
    # Gráfico 4: Comparación de precios actuales por contrato
    plt.subplot(2, 3, 4)
    latest_prices = []
    contract_labels = []
    contract_colors = []
    
    for symbol in monthly_df['symbol'].unique():
        symbol_data = monthly_df[monthly_df['symbol'] == symbol]
        latest = symbol_data.iloc[-1]
        
        latest_prices.append(latest['close_avg'])
        contract_labels.append(symbol)
        
        if latest['is_2026_projection']:
            contract_colors.append('green')
        else:
            contract_colors.append('blue')
    
    bars = plt.bar(contract_labels, latest_prices, color=contract_colors, alpha=0.7)
    plt.title(f'{commodity} - Precios Actuales por Contrato\n(Verde = Proyección 2026)')
    plt.xlabel('Contrato')
    plt.ylabel('Precio ($)')
    plt.xticks(rotation=45)
    
    # Añadir valores en las barras
    for bar, price in zip(bars, latest_prices):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'${price:.0f}', ha='center', va='bottom', fontweight='bold')
    plt.grid(True, alpha=0.3)
    
    # Gráfico 5: Análisis de tendencia (últimos 6 meses)
    plt.subplot(2, 3, 5)
    
    # Calcular tendencias para contratos 2026
    projection_symbols = [s for s in monthly_df['symbol'].unique() 
                         if s.endswith(('.c.3', '.c.4', '.c.5'))]
    
    trends = []
    trend_labels = []
    
    for symbol in projection_symbols:
        symbol_data = monthly_df[monthly_df['symbol'] == symbol]
        
        if len(symbol_data) >= 3:  # Necesitamos al menos 3 puntos
            recent_data = symbol_data.tail(6)['close_avg'].values
            x = range(len(recent_data))
            
            if len(recent_data) > 1:
                # Calcular pendiente de tendencia
                slope = np.polyfit(x, recent_data, 1)[0]
                trends.append(slope)
                trend_labels.append(symbol)
    
    if trends:
        colors_trend = ['green' if t > 0 else 'red' for t in trends]
        bars_trend = plt.bar(trend_labels, trends, color=colors_trend, alpha=0.7)
        plt.title(f'{commodity} - Tendencias 2026\n(Verde=Alcista, Rojo=Bajista)')
        plt.xlabel('Contrato 2026')
        plt.ylabel('Pendiente de Tendencia ($/mes)')
        plt.xticks(rotation=45)
        plt.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        plt.grid(True, alpha=0.3)
    
    # Gráfico 6: Resumen de oportunidades 2026
    plt.subplot(2, 3, 6)
    
    # Crear tabla de resumen
    summary_data = []
    for symbol in projection_symbols:
        symbol_data = monthly_df[monthly_df['symbol'] == symbol]
        if not symbol_data.empty:
            latest = symbol_data.iloc[-1]
            summary_data.append([
                symbol,
                f"${latest['close_avg']:.2f}",
                f"${latest['diff']:.2f}",
                f"${latest['range_avg']:.2f}"
            ])
    
    if summary_data:
        table = plt.table(cellText=summary_data,
                         colLabels=['Contrato 2026', 'Precio Actual', 'Diff Mensual', 'Volatilidad'],
                         cellLoc='center',
                         loc='center',
                         bbox=[0, 0, 1, 1])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        plt.axis('off')
        plt.title(f'{commodity} - Resumen Oportunidades 2026', pad=20)
    
    plt.tight_layout()
    plt.show()

def main():
    """Función principal"""
    commodity = "ZC"  # Maíz
    
    print("🚀 ANÁLISIS MENSUAL EXTENDIDO - PROYECCIONES HACIA 2026")
    print("="*60)
    
    # Realizar análisis
    monthly_data = monthly_futures_analysis(
        commodity=commodity,
        start_date="2024-01-01",
        end_date="2025-10-23"
    )
    
    if monthly_data is not None:
        # Crear resumen
        summary = create_extended_summary(monthly_data, commodity)
        
        if summary is not None:
            print(f"\n📋 TABLA RESUMEN - CONTRATOS {commodity} (FORMATO SOLICITADO):")
            print("="*80)
            print(f"{'Contrato':<12} {'Mes':<8} {'Open Avg':<12} {'Close Avg':<12} {'Diff':<10} {'2026?':<8}")
            print("-" * 80)
            
            for _, row in summary.iterrows():
                status = "⭐ SÍ" if row['is_2026'] else "❌ No"
                print(f"{row['contract']:<12} {row['latest_month']:<8} "
                      f"${row['open_avg']:<11.2f} ${row['close_avg']:<11.2f} "
                      f"${row['diff']:<9.2f} {status:<8}")
            
            print("\n🎯 INTERPRETACIÓN:")
            proyecciones_2026 = summary[summary['is_2026'] == True]
            if not proyecciones_2026.empty:
                print(f"✅ Encontraste {len(proyecciones_2026)} contratos con exposición a 2026:")
                for _, row in proyecciones_2026.iterrows():
                    trend = "📈 Alcista" if row['diff'] > 0 else "📉 Bajista"
                    print(f"   • {row['contract']}: ${row['close_avg']:.2f} - {trend}")
            
            print(f"\n💡 VENTAJAS vs monthly_avg_diff.py original:")
            print(f"   • Original: Solo 3 meses de 2025")
            print(f"   • Nuevo: {len(summary)} contratos extendidos hacia 2026")
            print(f"   • Proyecciones reales de precios futuros disponibles")
            print(f"   • Análisis de curva de futuros incluido")
            
            # Crear visualizaciones
            visualize_extended_analysis(monthly_data, commodity)
            
            # Guardar resultados
            output_file = f"{commodity}_monthly_extended_2026.csv"
            monthly_data.to_csv(output_file, index=False)
            print(f"\n💾 Datos guardados en: {output_file}")
            
        else:
            print("❌ No se pudo crear el resumen")
    else:
        print("❌ No se pudieron obtener los datos")

if __name__ == "__main__":
    main()

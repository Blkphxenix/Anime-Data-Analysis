"""
================================================================================
ANÁLISIS EXPLORATORIO DE DATOS (EDA) - DATASET DE ANIME 2026
================================================================================
Módulo de análisis estadístico y visualización para el catálogo histórico de 
MyAnimeList (MAL).

Funcionalidades principales:
- Ingesta y saneamiento de datos (normalización de nulos y casteo de tipos).
- Resumen descriptivo univariado y multivariado.
- Extracción temporal y análisis de tendencias históricas (1970 - 2026).
- Benchmark de estudios de animación y géneros narrativos.
- Exportación automatizada de figuras estadísticas en alta resolución.

Requisitos:
    pandas, numpy, matplotlib, seaborn
================================================================================
"""

import os
import re
from typing import Tuple
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def configure_visual_style() -> None:
    """Configura el tema global y parámetros tipográficos para Matplotlib y Seaborn."""
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
    plt.rcParams['figure.dpi'] = 150
    plt.rcParams['axes.titlesize'] = 13
    plt.rcParams['axes.titleweight'] = 'bold'
    plt.rcParams['axes.labelsize'] = 11


def load_dataset(csv_path: str) -> pd.DataFrame:
    """
    Carga el archivo CSV del dataset de anime.

    Args:
        csv_path (str): Ruta absoluta o relativa al archivo CSV.

    Returns:
        pd.DataFrame: DataFrame con los datos originales cargados.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"No se encontró el archivo de datos en: {csv_path}")
    
    print(f"[INFO] Cargando dataset desde: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"[INFO] Registros cargados: {df.shape[0]:,} filas x {df.shape[1]} columnas\n")
    return df


def extract_release_year(row: pd.Series) -> float:
    """
    Extrae el año de estreno a partir de las columnas 'Premiered' o 'Aired'.

    Args:
        row (pd.Series): Fila individual del DataFrame.

    Returns:
        float: Año en formato numérico entero (ej. 2021.0) o np.nan si no se detecta.
    """
    if pd.notna(row.get('Premiered')):
        match = re.search(r'\b(19\d\d|20\d\d)\b', str(row['Premiered']))
        if match:
            return float(match.group(1))
    if pd.notna(row.get('Aired')):
        match = re.search(r'\b(19\d\d|20\d\d)\b', str(row['Aired']))
        if match:
            return float(match.group(1))
    return np.nan


def clean_and_preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sanea el dataset reemplazando centinelas textuales ('UNKNOWN') por NaN, 
    casteando columnas cuantitativas a tipos numéricos e infiriendo el año de emisión.

    Args:
        df (pd.DataFrame): DataFrame crudo.

    Returns:
        pd.DataFrame: DataFrame procesado y listo para análisis.
    """
    print("[INFO] Limpiando y transformando variables...")
    cleaned_df = df.copy()

    # Columnas cuantitativas a convertir
    numeric_columns = ['Score', 'Episodes', 'Rank', 'Scored By']
    for col in numeric_columns:
        if col in cleaned_df.columns:
            cleaned_df[col] = pd.to_numeric(cleaned_df[col].replace('UNKNOWN', np.nan), errors='coerce')

    # Columnas categóricas y descriptivas
    text_columns = ['English name', 'Other name', 'Genres', 'Synopsis', 'Premiered', 
                    'Producers', 'Licensors', 'Studios', 'Source', 'Duration', 'Rating']
    for col in text_columns:
        if col in cleaned_df.columns:
            cleaned_df[col] = cleaned_df[col].replace('UNKNOWN', np.nan)

    # Inferencia del año de estreno
    cleaned_df['Year'] = cleaned_df.apply(extract_release_year, axis=1)

    print(f"  - Animes con calificación válida: {cleaned_df['Score'].notna().sum():,}")
    print(f"  - Animes con año detectado: {cleaned_df['Year'].notna().sum():,}\n")
    return cleaned_df


def save_plot(fig: plt.Figure, output_dir: str, filename: str) -> None:
    """
    Guarda una figura de matplotlib en formato PNG optimizado.

    Args:
        fig (plt.Figure): Objeto Figure a guardar.
        output_dir (str): Directorio de destino.
        filename (str): Nombre del archivo resultante (ej. '01_plot.png').
    """
    os.makedirs(output_dir, exist_ok=True)
    target_path = os.path.join(output_dir, filename)
    fig.savefig(target_path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(f"  [GUARDADO] {filename}")


def generate_all_visualizations(df: pd.DataFrame, output_dir: str) -> None:
    """
    Genera el paquete completo de 8 gráficos estadísticos para el informe EDA.

    Args:
        df (pd.DataFrame): DataFrame preprocesado.
        output_dir (str): Directorio donde se almacenarán las imágenes PNG.
    """
    print(f"[INFO] Generando visualizaciones en: {output_dir}")

    # 1. Distribución de Calificaciones
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    scores = df['Score'].dropna()
    sns.histplot(scores, bins=40, kde=True, color='#3498db', ax=ax1, edgecolor='black', alpha=0.6)
    ax1.axvline(scores.mean(), color='#e74c3c', linestyle='--', linewidth=2, label=f'Media: {scores.mean():.2f}')
    ax1.axvline(scores.median(), color='#2ecc71', linestyle='-', linewidth=2, label=f'Mediana: {scores.median():.2f}')
    ax1.set_title('Distribución de Calificaciones (Score)')
    ax1.set_xlabel('Score')
    ax1.set_ylabel('Frecuencia')
    ax1.legend()
    sns.boxplot(y=scores, color='#85c1e9', ax=ax2, width=0.3, flierprops=dict(markersize=2, alpha=0.3))
    ax2.set_title('Diagrama de Caja de Score')
    save_plot(fig, output_dir, '01_distribucion_score.png')

    # 2. Formato de Emisión
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5.5))
    type_counts = df['Type'].value_counts().head(7)
    bars = ax1.bar(type_counts.index, type_counts.values, color=sns.color_palette("mako", len(type_counts)), edgecolor='black')
    ax1.set_title('Volumen de Producción por Formato (Type)')
    ax1.set_ylabel('Cantidad de Obras')
    ax1.tick_params(axis='x', rotation=30)
    for bar in bars:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, yval + 100, f'{yval:,}', ha='center', va='bottom', fontsize=9)
    top_types = type_counts.index.tolist()
    df_type_scores = df[df['Type'].isin(top_types) & df['Score'].notna()]
    sns.boxplot(data=df_type_scores, x='Type', y='Score', order=top_types, palette="mako", ax=ax2, width=0.5, flierprops=dict(markersize=2, alpha=0.2))
    ax2.set_title('Distribución de Score por Formato')
    ax2.tick_params(axis='x', rotation=30)
    save_plot(fig, output_dir, '02_analisis_formatos.png')

    # 3. Evolución Histórica
    fig, ax1 = plt.subplots(figsize=(13, 6))
    yearly = df[(df['Year'] >= 1970) & (df['Year'] <= 2025)].groupby('Year').agg(
        count=('anime_id', 'count'), mean_score=('Score', 'mean')
    ).reset_index()
    c1, c2 = '#2980b9', '#e67e22'
    ax1.plot(yearly['Year'], yearly['count'], color=c1, marker='o', markersize=3, linewidth=2, label='Producción Anual')
    ax1.fill_between(yearly['Year'], yearly['count'], color=c1, alpha=0.15)
    ax1.set_xlabel('Año de Emisión')
    ax1.set_ylabel('Cantidad de Animes', color=c1)
    ax1.tick_params(axis='y', labelcolor=c1)
    ax2 = ax1.twinx()
    ax2.plot(yearly['Year'], yearly['mean_score'], color=c2, linestyle='--', linewidth=2.5, label='Score Promedio')
    ax2.set_ylabel('Score Promedio', color=c2)
    ax2.tick_params(axis='y', labelcolor=c2)
    ax2.grid(False)
    plt.title('Evolución Histórica de la Industria del Anime (1970 - 2025)')
    save_plot(fig, output_dir, '03_evolucion_historica.png')

    # 4. Top Géneros y Temáticas
    genres_df = df[['anime_id', 'Score', 'Genres']].dropna(subset=['Genres', 'Score'])
    genres_series = genres_df.assign(Genre=genres_df['Genres'].str.split(', ')).explode('Genre')
    genre_stats = genres_series.groupby('Genre').agg(count=('Score', 'count'), mean_score=('Score', 'mean'))
    top15_freq = genre_stats.sort_values(by='count', ascending=False).head(15)
    top15_rated = genre_stats[genre_stats['count'] >= 60].sort_values(by='mean_score', ascending=False).head(15)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    sns.barplot(y=top15_freq.index, x=top15_freq['count'], palette='viridis', ax=ax1, edgecolor='black')
    ax1.set_title('Top 15 Géneros Más Producidos')
    ax1.set_xlabel('Cantidad de Animes')
    for i, v in enumerate(top15_freq['count']):
        ax1.text(v + 50, i, f'{v:,}', va='center', fontsize=9)
    sns.barplot(y=top15_rated.index, x=top15_rated['mean_score'], palette='rocket', ax=ax2, edgecolor='black')
    ax2.set_title('Top 15 Géneros Mejor Calificados (mín. 60 animes)')
    ax2.set_xlabel('Score Promedio')
    ax2.set_xlim(6.5, 7.8)
    for i, v in enumerate(top15_rated['mean_score']):
        ax2.text(v + 0.02, i, f'{v:.2f}', va='center', fontsize=9)
    save_plot(fig, output_dir, '04_top_generos.png')

    # 5. Benchmark de Estudios
    studios_df = df[['anime_id', 'Score', 'Members', 'Studios']].dropna(subset=['Studios', 'Score'])
    studios_series = studios_df.assign(Studio=studios_df['Studios'].str.split(', ')).explode('Studio')
    studio_stats = studios_series.groupby('Studio').agg(
        count=('Score', 'count'), mean_score=('Score', 'mean'), total_members=('Members', 'sum')
    )
    major_studios = studio_stats[studio_stats['count'] >= 25].sort_values(by='mean_score', ascending=False)
    fig, ax = plt.subplots(figsize=(14, 8))
    scatter = ax.scatter(major_studios['count'], major_studios['mean_score'],
                         s=np.sqrt(major_studios['total_members'])/25, c=major_studios['mean_score'],
                         cmap='viridis', alpha=0.75, edgecolors='black', linewidth=1.2)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Score Promedio')
    ax.set_title('Benchmark de Estudios: Cantidad de Obras vs Calidad Media (mín. 25 animes)', pad=15)
    ax.set_xlabel('Cantidad de Animes Calificados')
    ax.set_ylabel('Score Promedio')
    destacados = {'Toei Animation': (-40, -18), 'Sunrise': (10, 5), 'J.C.Staff': (10, -10),
                  'Production I.G': (10, 5), 'Madhouse': (10, 5), 'Kyoto Animation': (10, 5),
                  'Bones': (10, -12), 'ufotable': (10, -5), 'MAPPA': (10, 5), 'A-1 Pictures': (10, 5),
                  'David Production': (10, 5), 'Studio Pierrot': (10, -15), 'White Fox': (10, -8),
                  'Wit Studio': (10, 5)}
    for std, (ox, oy) in destacados.items():
        if std in major_studios.index:
            ax.annotate(std, (major_studios.loc[std, 'count'], major_studios.loc[std, 'mean_score']),
                        xytext=(ox, oy), textcoords='offset points', fontsize=9, fontweight='bold',
                        bbox=dict(boxstyle="round,pad=0.25", fc="#fef9e7", alpha=0.85, ec="#d4ac0d", lw=0.8))
    save_plot(fig, output_dir, '05_benchmark_estudios.png')

    # 6. Matriz de Correlación
    fig, ax = plt.subplots(figsize=(9, 7))
    corr_cols = ['Score', 'Rank', 'Popularity', 'Members', 'Favorites', 'Scored By', 'Episodes']
    corr = df[corr_cols].corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='vlag', vmin=-1, vmax=1, center=0,
                square=True, linewidths=.8, ax=ax)
    ax.set_title('Matriz de Correlación Numérica', pad=15)
    save_plot(fig, output_dir, '06_matriz_correlacion.png')

    # 7. Top 10 Animes
    top_pop = df.sort_values(by='Members', ascending=False).head(10)
    top_scr = df[df['Scored By'] >= 10000].sort_values(by='Score', ascending=False).head(10)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 11))
    plt.subplots_adjust(hspace=0.35)
    sns.barplot(y='Name', x=top_pop['Members']/1e6, data=top_pop, hue='Name', legend=False, palette='Blues_r', ax=ax1, edgecolor='black')
    ax1.set_title('Top 10 Animes Más Populares por Número de Miembros (MAL)', fontsize=13, fontweight='bold')
    ax1.set_xlabel('Miembros (Millones)')
    ax1.set_ylabel('')
    ax1.set_xlim(0, 5.0)
    for i, v in enumerate(top_pop['Members']/1e6):
        ax1.text(v + 0.05, i, f'{v:.2f} M ({top_pop["Score"].iloc[i]:.2f} ★)', va='center', fontsize=9, fontweight='bold')
    sns.barplot(y='Name', x='Score', data=top_scr, hue='Name', legend=False, palette='Reds_r', ax=ax2, edgecolor='black')
    ax2.set_title('Top 10 Animes Mejor Calificados (mínimo 10,000 votos)', fontsize=13, fontweight='bold')
    ax2.set_xlabel('Score')
    ax2.set_ylabel('')
    ax2.set_xlim(8.8, 9.4)
    for i, v in enumerate(top_scr['Score']):
        ax2.text(v + 0.01, i, f'{v:.2f} ★ ({top_scr["Members"].iloc[i]:,} miembros)', va='center', fontsize=9, fontweight='bold')
    save_plot(fig, output_dir, '07_top_animes.png')

    # 8. Fuente de Adaptación
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    source_counts = df['Source'].value_counts().head(8)
    sns.barplot(y=source_counts.index, x=source_counts.values, palette='magma', ax=ax1, edgecolor='black')
    ax1.set_title('Top 8 Fuentes de Adaptación (Source)')
    ax1.set_xlabel('Cantidad de Animes')
    top_sources = source_counts.index.tolist()
    df_source_score = df[df['Source'].isin(top_sources) & df['Score'].notna()]
    sns.boxplot(data=df_source_score, y='Source', x='Score', order=top_sources, palette='magma', ax=ax2, width=0.5, flierprops=dict(markersize=2, alpha=0.2))
    ax2.set_title('Distribución de Calificaciones por Fuente de Adaptación')
    save_plot(fig, output_dir, '08_fuente_adaptacion.png')


def print_summary_statistics(df: pd.DataFrame) -> None:
    """Imprime un resumen estadístico estructurado en la consola."""
    print("="*60)
    print("RESUMEN ESTADÍSTICO DE VARIABLES NUMÉRICAS")
    print("="*60)
    numeric_df = df[['Score', 'Episodes', 'Rank', 'Popularity', 'Favorites', 'Scored By', 'Members']]
    print(numeric_df.describe().to_string())
    print("\n" + "="*60 + "\n")


def main() -> None:
    """Punto de entrada principal para la ejecución del pipeline EDA."""
    configure_visual_style()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.join(base_dir, 'anime-dataset-2026.csv')
    plots_folder = os.path.join(base_dir, 'eda_plots')

    raw_data = load_dataset(csv_file)
    clean_data = clean_and_preprocess(raw_data)
    print_summary_statistics(clean_data)
    generate_all_visualizations(clean_data, plots_folder)

    print("="*60)
    print(f"Directorio de salida: {plots_folder}")
    print("="*60)


if __name__ == '__main__':
    main()
